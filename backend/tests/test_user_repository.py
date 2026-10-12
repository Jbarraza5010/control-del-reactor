"""Pruebas de contrato: las DOS implementaciones del repositorio deben comportarse igual."""
import pytest

from app.infrastructure.persistence.memory.in_memory_user_repository import InMemoryUserRepository
from app.shared.errors import ConflictError
from tests.conftest import make_user


@pytest.fixture(params=["memoria", "sql"])
def repo(request, sql_repository):
    return InMemoryUserRepository() if request.param == "memoria" else sql_repository


def test_guarda_y_recupera_por_id_correo_y_usuario(repo):
    repo.save(make_user())
    assert repo.find_by_id("1").username == "Ulfran"
    assert repo.find_by_email("ulfran@TEC.ac.cr").id == "1"  # el correo no distingue mayúsculas
    assert repo.find_by_username("Ulfran").id == "1"


def test_devuelve_none_cuando_no_existe(repo):
    assert repo.find_by_id("x") is None
    assert repo.find_by_email("nadie@tec.ac.cr") is None
    assert repo.find_by_username("nadie") is None


def test_save_actualiza_un_usuario_existente(repo):
    repo.save(make_user())
    repo.save(make_user(status="ACTIVA"))
    assert repo.find_by_id("1").status == "ACTIVA"


def test_sql_rechaza_correo_duplicado(sql_repository):
    sql_repository.save(make_user())
    with pytest.raises(ConflictError):
        sql_repository.save(make_user(id="2", username="Otro"))  # mismo correo


def test_sql_rechaza_usuario_duplicado(sql_repository):
    sql_repository.save(make_user())
    with pytest.raises(ConflictError):
        sql_repository.save(make_user(id="2", email="otro@tec.ac.cr"))  # mismo usuario
