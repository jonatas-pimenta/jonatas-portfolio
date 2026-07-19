import argparse
import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from backend.database import EstoqueDB
from scripts.backup_offsite import (
    _create_tar_gz,
    _decrypt_to_archive,
    _encrypt_archive,
    _extract_db_from_archive,
    run_validate_restore,
    upload_encrypted_backup,
)


class TestDatabaseCoreFlows(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.db_file = self.temp_path / "estoque_test.db"
        self.db = EstoqueDB(str(self.db_file))

    def tearDown(self):
        self.db.fechar_conexao()
        self.temp_dir.cleanup()

    def test_fornecedor_crud(self):
        created = self.db.criar_fornecedor(
            nome="Fornecedor A",
            telefone_celular="11999999999",
            telefone_fixo="1133334444",
            email="fornecedor@example.com",
            endereco="Rua A, 10",
            observacao="Prioritario",
        )
        self.assertTrue(created)

        fornecedores = self.db.listar_fornecedores()
        self.assertEqual(1, len(fornecedores))
        self.assertEqual("Fornecedor A", fornecedores[0]["nome"])

        updated = self.db.atualizar_fornecedor(
            "Fornecedor A",
            novo_nome="Fornecedor B",
            telefone_celular="11888888888",
        )
        self.assertTrue(updated)

        fornecedores = self.db.listar_fornecedores()
        self.assertEqual("Fornecedor B", fornecedores[0]["nome"])
        self.assertEqual("11888888888", fornecedores[0]["telefone_celular"])

        deleted = self.db.deletar_fornecedor("Fornecedor B")
        self.assertTrue(deleted)
        self.assertEqual([], self.db.listar_fornecedores())

    def test_cliente_crud(self):
        self.assertTrue(self.db.criar_cliente(nome="Cliente A", email="cliente@example.com"))

        clientes = self.db.listar_clientes()
        self.assertEqual(1, len(clientes))
        self.assertEqual("Cliente A", clientes[0]["nome"])

        self.assertTrue(
            self.db.atualizar_cliente(
                "Cliente A",
                novo_nome="Cliente B",
                telefone_fixo="1130303030",
            )
        )

        clientes = self.db.listar_clientes()
        self.assertEqual("Cliente B", clientes[0]["nome"])
        self.assertEqual("1130303030", clientes[0]["telefone_fixo"])

        self.assertTrue(self.db.deletar_cliente("Cliente B"))
        self.assertEqual([], self.db.listar_clientes())

    def test_movimentacao_historico_mantem_produto_removido(self):
        self.assertTrue(
            self.db.criar_produto(
                nome="Mouse USB",
                categoria="Perifericos",
                preco=50.0,
                quantidade=10,
                estoque_minimo=2,
                fornecedor="Fornecedor X",
            )
        )

        # Use default active user created by bootstrap.
        self.assertTrue(
            self.db.registrar_movimentacao(
                nome_produto="Mouse USB",
                tipo_movimento="saida",
                quantidade=2,
                observacao="Venda teste",
                usuario="Operador1",
            )
        )

        self.assertTrue(self.db.deletar_produto("Mouse USB"))

        movimentos = self.db.listar_movimentacoes(limite=10)
        self.assertEqual(1, len(movimentos))
        self.assertEqual("Produto removido", movimentos[0]["produto_nome"])
        self.assertEqual("Operador1", movimentos[0]["usuario"])


class TestBackupCoreFlows(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        self.db_file = self.temp_path / "origem.db"
        self._create_sample_db(self.db_file)

        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()

        self.private_key_path = self.temp_path / "backup_private.pem"
        self.public_key_path = self.temp_path / "backup_public.pem"

        self.private_key_path.write_bytes(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
        self.public_key_path.write_bytes(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    @staticmethod
    def _create_sample_db(path: Path):
        con = sqlite3.connect(str(path))
        try:
            con.execute("CREATE TABLE sample (id INTEGER PRIMARY KEY, nome TEXT NOT NULL)")
            con.execute("INSERT INTO sample (nome) VALUES (?)", ("registro_teste",))
            con.commit()
        finally:
            con.close()

    @staticmethod
    def _sha256(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def test_encrypt_decrypt_extract_roundtrip(self):
        archive_path = self.temp_path / "backup.tar.gz"
        encrypted_path = self.temp_path / "backup.enc.json"
        restored_archive = self.temp_path / "restored.tar.gz"
        restored_db = self.temp_path / "restored.db"

        _create_tar_gz(self.db_file, archive_path)
        self.assertTrue(archive_path.exists())

        checksum = _encrypt_archive(archive_path, self.public_key_path, encrypted_path)
        self.assertEqual(64, len(checksum))
        self.assertTrue(encrypted_path.exists())

        recovered_checksum = _decrypt_to_archive(
            encrypted_file_path=encrypted_path,
            private_key_path=self.private_key_path,
            private_key_passphrase=None,
            archive_output_path=restored_archive,
        )
        self.assertEqual(checksum, recovered_checksum)

        _extract_db_from_archive(restored_archive, restored_db)
        self.assertTrue(restored_db.exists())
        self.assertEqual(self._sha256(self.db_file), self._sha256(restored_db))

    def test_validate_restore_returns_zero(self):
        archive_path = self.temp_path / "backup.tar.gz"
        encrypted_path = self.temp_path / "backup.enc.json"

        _create_tar_gz(self.db_file, archive_path)
        _encrypt_archive(archive_path, self.public_key_path, encrypted_path)

        args = argparse.Namespace(
            encrypted_file=str(encrypted_path),
            private_key=str(self.private_key_path),
            private_key_passphrase=None,
            test_restore_dir=str(self.temp_path / "restore_test"),
            log_file=str(self.temp_path / "backup_offsite.log"),
        )
        self.assertEqual(0, run_validate_restore(args))

    @patch("scripts.backup_offsite._upload_to_drive", return_value="file_123")
    @patch("scripts.backup_offsite._build_drive_service_oauth_user", return_value=object())
    def test_upload_encrypted_backup_oauth_mode(self, mock_build_oauth, mock_upload):
        encrypted_path = self.temp_path / "dummy.enc.json"
        encrypted_path.write_text("{}", encoding="utf-8")

        file_id = upload_encrypted_backup(
            encrypted_file_path=encrypted_path,
            drive_folder_id=None,
            drive_auth_mode="oauth_user",
            drive_oauth_client_secret_json=self.temp_path / "cred_oauth.json",
            drive_oauth_token_json=self.temp_path / "token.json",
        )

        self.assertEqual("file_123", file_id)
        mock_build_oauth.assert_called_once()
        mock_upload.assert_called_once()

    def test_upload_encrypted_backup_service_account_requires_folder(self):
        encrypted_path = self.temp_path / "dummy.enc.json"
        encrypted_path.write_text("{}", encoding="utf-8")

        with self.assertRaises(ValueError):
            upload_encrypted_backup(
                encrypted_file_path=encrypted_path,
                drive_folder_id=None,
                drive_auth_mode="service_account",
                drive_service_account_json=self.temp_path / "service.json",
            )


if __name__ == "__main__":
    unittest.main()
