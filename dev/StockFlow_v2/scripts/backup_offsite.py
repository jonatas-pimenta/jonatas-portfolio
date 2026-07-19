#!/usr/bin/env python3
"""Backup off-site com criptografia hibrida e upload opcional no Google Drive.

Fluxo de backup:
1) Compacta o banco SQLite em .tar.gz
2) Criptografa o arquivo com AES-256-GCM
3) Protege a chave AES usando RSA-OAEP (chave publica)
4) Salva envelope criptografado em JSON
5) Opcionalmente envia para Google Drive (service account)

Fluxo de restauracao:
1) Le envelope criptografado JSON
2) Descriptografa a chave AES com RSA privada
3) Descriptografa o conteudo AES-GCM
4) Extrai o .db de volta para disco
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
import logging
import mimetypes
import os
import pathlib
import shutil
import sqlite3
import sys
import tarfile
import tempfile
from typing import Optional
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def _is_oauth_invalid_grant_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return "invalid_grant" in msg or "expired or revoked" in msg


def _is_oauth_access_denied_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return "access_denied" in msg or "not completed the google verification process" in msg


def _is_service_account_quota_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return "storagequotaexceeded" in msg or "service accounts do not have storage quota" in msg


def _setup_logger(log_file: pathlib.Path) -> logging.Logger:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("backup_offsite")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    stream_handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s", "%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def _read_bytes(path: pathlib.Path) -> bytes:
    with path.open("rb") as f:
        return f.read()


def _write_bytes(path: pathlib.Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        f.write(data)


def _b64e(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def _b64d(data: str) -> bytes:
    return base64.b64decode(data.encode("ascii"))


def _load_public_key(public_key_path: pathlib.Path):
    public_pem = _read_bytes(public_key_path)
    return serialization.load_pem_public_key(public_pem)


def _load_private_key(private_key_path: pathlib.Path, passphrase: Optional[str]):
    private_pem = _read_bytes(private_key_path)
    password_bytes = passphrase.encode("utf-8") if passphrase else None
    return serialization.load_pem_private_key(private_pem, password=password_bytes)


def _create_tar_gz(db_path: pathlib.Path, archive_path: pathlib.Path) -> None:
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(db_path, arcname=db_path.name)


def _encrypt_archive(
    archive_path: pathlib.Path,
    public_key_path: pathlib.Path,
    encrypted_output_path: pathlib.Path,
) -> str:
    plaintext = _read_bytes(archive_path)
    aes_key = os.urandom(32)
    nonce = os.urandom(12)

    aesgcm = AESGCM(aes_key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data=None)

    public_key = _load_public_key(public_key_path)
    wrapped_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    checksum = hashlib.sha256(ciphertext).hexdigest()

    envelope = {
        "version": "1",
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "algorithms": {
            "content_encryption": "AES-256-GCM",
            "key_wrapping": "RSA-OAEP-SHA256",
        },
        "payload": {
            "wrapped_aes_key_b64": _b64e(wrapped_key),
            "nonce_b64": _b64e(nonce),
            "ciphertext_b64": _b64e(ciphertext),
            "ciphertext_sha256": checksum,
            "archive_name": archive_path.name,
        },
    }

    encrypted_output_path.parent.mkdir(parents=True, exist_ok=True)
    with encrypted_output_path.open("w", encoding="utf-8") as f:
        json.dump(envelope, f, ensure_ascii=True, indent=2)

    return checksum


def _decrypt_to_archive(
    encrypted_file_path: pathlib.Path,
    private_key_path: pathlib.Path,
    private_key_passphrase: Optional[str],
    archive_output_path: pathlib.Path,
) -> str:
    with encrypted_file_path.open("r", encoding="utf-8") as f:
        envelope = json.load(f)

    payload = envelope["payload"]
    wrapped_key = _b64d(payload["wrapped_aes_key_b64"])
    nonce = _b64d(payload["nonce_b64"])
    ciphertext = _b64d(payload["ciphertext_b64"])
    expected_checksum = payload["ciphertext_sha256"]

    actual_checksum = hashlib.sha256(ciphertext).hexdigest()
    if actual_checksum != expected_checksum:
        raise ValueError("Checksum SHA256 do payload criptografado nao confere")

    private_key = _load_private_key(private_key_path, private_key_passphrase)
    aes_key = private_key.decrypt(
        wrapped_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    aesgcm = AESGCM(aes_key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data=None)

    _write_bytes(archive_output_path, plaintext)
    return actual_checksum


def _extract_db_from_archive(archive_path: pathlib.Path, output_db_path: pathlib.Path) -> pathlib.Path:
    with tarfile.open(archive_path, "r:gz") as tar:
        members = tar.getmembers()
        if not members:
            raise ValueError("Arquivo compactado vazio")

        db_members = [m for m in members if m.name.endswith(".db") and m.isfile()]
        if not db_members:
            raise ValueError("Nenhum arquivo .db encontrado no backup")

        member = db_members[0]
        extracted = tar.extractfile(member)
        if extracted is None:
            raise ValueError("Falha ao extrair arquivo .db do backup")

        output_db_path.parent.mkdir(parents=True, exist_ok=True)
        with output_db_path.open("wb") as out:
            shutil.copyfileobj(extracted, out)

    return output_db_path


def _upload_to_drive(
    drive_service,
    encrypted_file_path: pathlib.Path,
    folder_id: Optional[str],
    mime_type: Optional[str] = None,
) -> str:
    from googleapiclient.http import MediaFileUpload

    media_mime_type = mime_type or "application/octet-stream"
    metadata = {"name": encrypted_file_path.name}
    if folder_id:
        metadata["parents"] = [folder_id]

    media = MediaFileUpload(str(encrypted_file_path), mimetype=media_mime_type)
    created = (
        drive_service.files()
        .create(
            body=metadata,
            media_body=media,
            fields="id",
            supportsAllDrives=True,
        )
        .execute()
    )
    return created["id"]


def _build_drive_service_service_account(service_account_json: pathlib.Path):
    # Import local para manter o script executavel mesmo sem dependencias do Drive.
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    scopes = ["https://www.googleapis.com/auth/drive.file"]
    credentials = service_account.Credentials.from_service_account_file(
        str(service_account_json), scopes=scopes
    )
    return build("drive", "v3", credentials=credentials, cache_discovery=False)


def _build_drive_service_oauth_user(
    oauth_client_secret_json: pathlib.Path,
    oauth_token_json: pathlib.Path,
):
    # Import local para manter o script executavel mesmo sem dependencias do Drive.
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    scopes = ["https://www.googleapis.com/auth/drive.file"]
    creds = None

    if oauth_token_json.exists():
        creds = Credentials.from_authorized_user_file(str(oauth_token_json), scopes=scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as exc:
                if _is_oauth_invalid_grant_error(exc):
                    # Token revogado/expirado de forma irreversivel: remove e exige novo login.
                    try:
                        oauth_token_json.unlink(missing_ok=True)
                    except Exception:
                        pass
                    creds = None
                else:
                    raise

        if not creds or not creds.valid:
            if not oauth_client_secret_json.exists():
                raise FileNotFoundError(
                    f"Credencial OAuth de usuario nao encontrada: {oauth_client_secret_json}"
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(oauth_client_secret_json), scopes=scopes
            )
            try:
                creds = flow.run_local_server(port=0)
            except Exception as exc:
                if _is_oauth_access_denied_error(exc):
                    raise RuntimeError(
                        "OAuth bloqueado pelo Google (access_denied). "
                        "Adicione o e-mail atual como usuario de teste na tela de consentimento OAuth "
                        "ou publique/verifique o app no Google Cloud Console."
                    ) from exc
                raise

        oauth_token_json.parent.mkdir(parents=True, exist_ok=True)
        with oauth_token_json.open("w", encoding="utf-8") as token_file:
            token_file.write(creds.to_json())

    return build("drive", "v3", credentials=creds, cache_discovery=False)


def upload_encrypted_backup(
    encrypted_file_path: pathlib.Path,
    drive_folder_id: Optional[str],
    drive_auth_mode: str = "auto",
    drive_service_account_json: Optional[pathlib.Path] = None,
    drive_oauth_client_secret_json: Optional[pathlib.Path] = None,
    drive_oauth_token_json: Optional[pathlib.Path] = None,
) -> str:
    """Envia um backup criptografado existente (.enc.json) para o Google Drive.

    Retorna o file_id em caso de sucesso e levanta excecao em caso de falha.
    """
    if not encrypted_file_path.exists():
        raise FileNotFoundError(f"Arquivo criptografado nao encontrado: {encrypted_file_path}")

    modo = (drive_auth_mode or "auto").strip().lower()
    pasta_id = (drive_folder_id or "").strip() or None

    if modo == "auto":
        modo = "oauth_user" if drive_oauth_client_secret_json else "service_account"

    if modo == "oauth_user":
        oauth_client_secret_json = pathlib.Path(
            drive_oauth_client_secret_json or "credentials_oauth.json"
        )
        oauth_token_json = pathlib.Path(
            drive_oauth_token_json or "token_google_drive.json"
        )
        drive_service = _build_drive_service_oauth_user(
            oauth_client_secret_json=oauth_client_secret_json,
            oauth_token_json=oauth_token_json,
        )
        try:
            return _upload_to_drive(
                drive_service=drive_service,
                encrypted_file_path=encrypted_file_path,
                folder_id=pasta_id,
                mime_type="application/json",
            )
        except Exception as exc:
            if not _is_oauth_invalid_grant_error(exc):
                raise

            # Fallback: token ficou invalido apos o build; limpa e refaz o login OAuth.
            try:
                oauth_token_json.unlink(missing_ok=True)
            except Exception:
                pass

            drive_service = _build_drive_service_oauth_user(
                oauth_client_secret_json=oauth_client_secret_json,
                oauth_token_json=oauth_token_json,
            )
            return _upload_to_drive(
                drive_service=drive_service,
                encrypted_file_path=encrypted_file_path,
                folder_id=pasta_id,
                mime_type="application/json",
            )

    if modo == "service_account":
        if not pasta_id:
            raise ValueError("drive_folder_id nao informado para service_account")

        if not drive_service_account_json:
            raise ValueError("drive_service_account_json nao informado")

        cred_json = pathlib.Path(drive_service_account_json)
        if not cred_json.exists():
            raise FileNotFoundError(
                f"Credencial service account nao encontrada: {cred_json}"
            )

        drive_service = _build_drive_service_service_account(cred_json)
        try:
            return _upload_to_drive(
                drive_service=drive_service,
                encrypted_file_path=encrypted_file_path,
                folder_id=pasta_id,
                mime_type="application/json",
            )
        except Exception as exc:
            if _is_service_account_quota_error(exc):
                raise RuntimeError(
                    "Service account sem cota no Meu Drive. "
                    "Use uma pasta em Shared Drive e compartilhe com a service account; "
                    f"folder_id atual: {pasta_id}"
                ) from exc
            raise

    raise ValueError("drive_auth_mode invalido. Use: auto, service_account ou oauth_user")


def upload_file_to_drive(
    file_path: pathlib.Path,
    drive_folder_id: Optional[str],
    drive_auth_mode: str = "auto",
    drive_service_account_json: Optional[pathlib.Path] = None,
    drive_oauth_client_secret_json: Optional[pathlib.Path] = None,
    drive_oauth_token_json: Optional[pathlib.Path] = None,
) -> str:
    """Envia um arquivo qualquer para o Google Drive usando a mesma estrategia de autenticacao do backup."""
    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {file_path}")

    modo = (drive_auth_mode or "auto").strip().lower()
    pasta_id = (drive_folder_id or "").strip() or None

    if modo == "auto":
        modo = "oauth_user" if drive_oauth_client_secret_json else "service_account"

    mime_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"

    if modo == "oauth_user":
        oauth_client_secret_json = pathlib.Path(
            drive_oauth_client_secret_json or "credentials_oauth.json"
        )
        oauth_token_json = pathlib.Path(
            drive_oauth_token_json or "token_google_drive.json"
        )
        drive_service = _build_drive_service_oauth_user(
            oauth_client_secret_json=oauth_client_secret_json,
            oauth_token_json=oauth_token_json,
        )
        try:
            return _upload_to_drive(
                drive_service=drive_service,
                encrypted_file_path=file_path,
                folder_id=pasta_id,
                mime_type=mime_type,
            )
        except Exception as exc:
            if not _is_oauth_invalid_grant_error(exc):
                raise

            try:
                oauth_token_json.unlink(missing_ok=True)
            except Exception:
                pass

            drive_service = _build_drive_service_oauth_user(
                oauth_client_secret_json=oauth_client_secret_json,
                oauth_token_json=oauth_token_json,
            )
            return _upload_to_drive(
                drive_service=drive_service,
                encrypted_file_path=file_path,
                folder_id=pasta_id,
                mime_type=mime_type,
            )

    if modo == "service_account":
        if not pasta_id:
            raise ValueError("drive_folder_id nao informado para service_account")

        if not drive_service_account_json:
            raise ValueError("drive_service_account_json nao informado")

        cred_json = pathlib.Path(drive_service_account_json)
        if not cred_json.exists():
            raise FileNotFoundError(
                f"Credencial service account nao encontrada: {cred_json}"
            )

        drive_service = _build_drive_service_service_account(cred_json)
        try:
            return _upload_to_drive(
                drive_service=drive_service,
                encrypted_file_path=file_path,
                folder_id=pasta_id,
                mime_type=mime_type,
            )
        except Exception as exc:
            if _is_service_account_quota_error(exc):
                raise RuntimeError(
                    "Service account sem cota no Meu Drive. "
                    "Use uma pasta em Shared Drive e compartilhe com a service account; "
                    f"folder_id atual: {pasta_id}"
                ) from exc
            raise

    raise ValueError("drive_auth_mode invalido. Use: auto, service_account ou oauth_user")


def run_backup(args: argparse.Namespace) -> int:
    logger = _setup_logger(pathlib.Path(args.log_file))

    db_path = pathlib.Path(args.db_path)
    public_key_path = pathlib.Path(args.public_key)
    output_dir = pathlib.Path(args.output_dir)

    timestamp = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    archive_path = output_dir / f"estoque_backup_{timestamp}.tar.gz"
    encrypted_path = output_dir / f"estoque_backup_{timestamp}.enc.json"

    try:
        if not db_path.exists():
            raise FileNotFoundError(f"Banco nao encontrado: {db_path}")
        if not public_key_path.exists():
            raise FileNotFoundError(f"Chave publica nao encontrada: {public_key_path}")

        logger.info("Iniciando backup do banco: %s", db_path)
        _create_tar_gz(db_path, archive_path)
        logger.info("Arquivo compactado criado: %s", archive_path)

        checksum = _encrypt_archive(archive_path, public_key_path, encrypted_path)
        logger.info("Arquivo criptografado criado: %s", encrypted_path)
        logger.info("SHA256 payload criptografado: %s", checksum)

        drive_file_id = None
        drive_upload_failed = False
        drive_folder_id = (args.drive_folder_id or "").strip() or None
        drive_auth_mode = (args.drive_auth_mode or "auto").strip().lower()
        drive_requested = bool(
            args.drive_service_account_json
            or args.drive_oauth_client_secret_json
            or drive_auth_mode == "oauth_user"
        )

        if drive_requested:
            try:
                drive_file_id = upload_encrypted_backup(
                    encrypted_file_path=encrypted_path,
                    drive_folder_id=drive_folder_id,
                    drive_auth_mode=drive_auth_mode,
                    drive_service_account_json=(
                        pathlib.Path(args.drive_service_account_json)
                        if args.drive_service_account_json
                        else None
                    ),
                    drive_oauth_client_secret_json=(
                        pathlib.Path(args.drive_oauth_client_secret_json)
                        if args.drive_oauth_client_secret_json
                        else None
                    ),
                    drive_oauth_token_json=(
                        pathlib.Path(args.drive_oauth_token_json)
                        if args.drive_oauth_token_json
                        else pathlib.Path("token_google_drive.json")
                    ),
                )
                logger.info("Upload para Google Drive concluido. file_id=%s", drive_file_id)
            except Exception as exc:
                if args.strict_drive_upload:
                    raise
                drive_upload_failed = True
                logger.exception("Falha no upload para Google Drive: %s", exc)

        if drive_upload_failed:
            logger.warning("Backup local criptografado concluido, mas upload no Drive falhou")
            return 2

        logger.info("Backup finalizado com sucesso")
        return 0

    except Exception as exc:
        logger.exception("Falha no backup: %s", exc)
        return 1
    finally:
        # Garante limpeza do arquivo temporario mesmo se houver falha no upload.
        if not args.keep_plain_archive and archive_path.exists():
            try:
                archive_path.unlink()
                logger.info("Arquivo compactado temporario removido: %s", archive_path)
            except Exception:
                logger.warning("Nao foi possivel remover arquivo temporario: %s", archive_path)


def run_restore(args: argparse.Namespace) -> int:
    logger = _setup_logger(pathlib.Path(args.log_file))

    encrypted_file = pathlib.Path(args.encrypted_file)
    private_key = pathlib.Path(args.private_key)
    output_db = pathlib.Path(args.output_db)
    passphrase = args.private_key_passphrase or os.getenv("BACKUP_PRIVATE_KEY_PASSPHRASE")

    try:
        if not encrypted_file.exists():
            raise FileNotFoundError(f"Backup criptografado nao encontrado: {encrypted_file}")
        if not private_key.exists():
            raise FileNotFoundError(f"Chave privada nao encontrada: {private_key}")

        with tempfile.TemporaryDirectory(prefix="restore_") as temp_dir:
            temp_archive = pathlib.Path(temp_dir) / "restored_backup.tar.gz"
            checksum = _decrypt_to_archive(
                encrypted_file_path=encrypted_file,
                private_key_path=private_key,
                private_key_passphrase=passphrase,
                archive_output_path=temp_archive,
            )
            _extract_db_from_archive(temp_archive, output_db)

        logger.info("Restore concluido: %s", output_db)
        logger.info("SHA256 payload verificado: %s", checksum)
        return 0

    except Exception as exc:
        logger.exception("Falha no restore: %s", exc)
        return 1


def run_validate_restore(args: argparse.Namespace) -> int:
    logger = _setup_logger(pathlib.Path(args.log_file))

    encrypted_file = pathlib.Path(args.encrypted_file)
    private_key = pathlib.Path(args.private_key)
    passphrase = args.private_key_passphrase or os.getenv("BACKUP_PRIVATE_KEY_PASSPHRASE")

    restore_dir = pathlib.Path(args.test_restore_dir)
    restore_dir.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    restored_db = restore_dir / f"restore_teste_{timestamp}.db"

    try:
        restore_args = argparse.Namespace(
            encrypted_file=str(encrypted_file),
            private_key=str(private_key),
            output_db=str(restored_db),
            private_key_passphrase=passphrase,
            log_file=args.log_file,
        )
        restore_rc = run_restore(restore_args)
        if restore_rc != 0:
            raise RuntimeError("Falha na etapa de restauracao")

        con = sqlite3.connect(str(restored_db))
        try:
            result = con.execute("PRAGMA integrity_check;").fetchone()
            integrity = result[0] if result else "unknown"
        finally:
            con.close()

        if integrity != "ok":
            raise RuntimeError(f"PRAGMA integrity_check retornou: {integrity}")

        logger.info("Validacao concluida com sucesso. integrity_check=ok")
        logger.info("Banco restaurado para teste em: %s", restored_db)
        return 0

    except Exception as exc:
        logger.exception("Falha na validacao de restore: %s", exc)
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Backup off-site criptografado")
    sub = parser.add_subparsers(dest="command", required=True)

    backup = sub.add_parser("backup", help="Executa backup criptografado")
    backup.add_argument("--db-path", default="estoque.db", help="Caminho do banco SQLite")
    backup.add_argument("--output-dir", default="outputs/backups", help="Pasta dos backups")
    backup.add_argument(
        "--public-key",
        default="keys/backup_public.pem",
        help="Caminho da chave publica RSA (PEM)",
    )
    backup.add_argument(
        "--log-file",
        default="outputs/logs/backup_offsite.log",
        help="Arquivo de log",
    )
    backup.add_argument(
        "--keep-plain-archive",
        action="store_true",
        help="Mantem o .tar.gz local alem do arquivo criptografado",
    )
    backup.add_argument(
        "--drive-service-account-json",
        default=None,
        help="Credencial JSON de service account para upload no Drive",
    )
    backup.add_argument(
        "--drive-folder-id",
        default=None,
        help="ID da pasta destino no Google Drive (opcional)",
    )
    backup.add_argument(
        "--drive-auth-mode",
        choices=["auto", "service_account", "oauth_user"],
        default="auto",
        help="Modo de autenticacao no Drive",
    )
    backup.add_argument(
        "--drive-oauth-client-secret-json",
        default=None,
        help="Arquivo OAuth client secret (Desktop app) para upload no Meu Drive",
    )
    backup.add_argument(
        "--drive-oauth-token-json",
        default="token_google_drive.json",
        help="Arquivo para persistir token OAuth de usuario",
    )
    backup.add_argument(
        "--strict-drive-upload",
        action="store_true",
        help="Se habilitado, falha o backup quando o upload no Drive falhar",
    )
    backup.set_defaults(func=run_backup)

    restore = sub.add_parser("restore", help="Restaura backup criptografado para .db")
    restore.add_argument("--encrypted-file", required=True, help="Arquivo .enc.json")
    restore.add_argument("--private-key", required=True, help="Chave privada RSA (PEM)")
    restore.add_argument("--output-db", required=True, help="Caminho do banco restaurado")
    restore.add_argument(
        "--private-key-passphrase",
        default=None,
        help="Passphrase da chave privada (ou env BACKUP_PRIVATE_KEY_PASSPHRASE)",
    )
    restore.add_argument(
        "--log-file",
        default="outputs/logs/backup_offsite.log",
        help="Arquivo de log",
    )
    restore.set_defaults(func=run_restore)

    validate_restore = sub.add_parser(
        "validate-restore",
        help="Restaura em ambiente de teste e roda PRAGMA integrity_check",
    )
    validate_restore.add_argument("--encrypted-file", required=True, help="Arquivo .enc.json")
    validate_restore.add_argument("--private-key", required=True, help="Chave privada RSA (PEM)")
    validate_restore.add_argument(
        "--private-key-passphrase",
        default=None,
        help="Passphrase da chave privada (ou env BACKUP_PRIVATE_KEY_PASSPHRASE)",
    )
    validate_restore.add_argument(
        "--test-restore-dir",
        default="outputs/restore_test",
        help="Diretorio para restauracao de validacao",
    )
    validate_restore.add_argument(
        "--log-file",
        default="outputs/logs/backup_offsite.log",
        help="Arquivo de log",
    )
    validate_restore.set_defaults(func=run_validate_restore)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
