from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, persistence
from app.business.eol import eol_business
from app.notification.eol_notification_utils import EOL_WARNING_THRESHOLD_DAYS
from app.routers.pteams import bg_create_tags_from_sbom_json
from app.tests.medium.constants import (
    PTEAM1,
    USER1,
)
from app.tests.medium.utils import (
    create_pteam,
    create_user,
)
from app.utility.progress_logger import TimeBasedProgressLogger


@pytest.fixture(scope="function")
def service1(testdb: Session) -> models.Service:
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)

    service_name1 = "test_service1"
    upload_file_name = "trivy-ubuntu2004.cdx.json"
    sbom_file = (
        Path(__file__).resolve().parent.parent.parent / "common" / "upload_test" / upload_file_name
    )
    with open(sbom_file, "r") as sbom:
        sbom_json = sbom.read()

    bg_create_tags_from_sbom_json(sbom_json, pteam1.pteam_id, service_name1, upload_file_name)

    return testdb.scalars(
        select(models.Service).where(models.Service.service_name == service_name1)
    ).one()


@pytest.fixture(scope="function")
def service2(testdb: Session) -> models.Service:
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)

    service_name1 = "test_service2"
    upload_file_name = "sqlite-alpine.json"
    sbom_file = (
        Path(__file__).resolve().parent.parent.parent / "common" / "upload_test" / upload_file_name
    )
    with open(sbom_file, "r") as sbom:
        sbom_json = sbom.read()

    bg_create_tags_from_sbom_json(sbom_json, pteam1.pteam_id, service_name1, upload_file_name)

    return testdb.scalars(
        select(models.Service).where(models.Service.service_name == service_name1)
    ).one()


@pytest.fixture(scope="function")
def eol_product1(testdb: Session) -> models.EoLProduct:
    eol_product = models.EoLProduct(
        eol_product_id="eol_product_id_1",
        name="ubuntu",
        product_category=models.ProductCategoryEnum.OS,
        description="description_1",
        is_ecosystem=True,
        matching_name="ubuntu_dummy_name",
    )

    persistence.create_eol_product(testdb, eol_product)
    return eol_product


@pytest.fixture(scope="function")
def eol_product2(testdb: Session) -> models.EoLProduct:
    eol_product = models.EoLProduct(
        eol_product_id="eol_product_id_2",
        name="sqlite",
        product_category=models.ProductCategoryEnum.PACKAGE,
        description="description_2",
        is_ecosystem=False,
        matching_name="sqlite",
    )

    persistence.create_eol_product(testdb, eol_product)
    return eol_product


@pytest.fixture(scope="function")
def eol_version1(
    testdb: Session,
    eol_product1: models.EoLProduct,
) -> models.EoLVersion:

    now = datetime.now(timezone.utc)
    eol_version1 = models.EoLVersion(
        eol_product_id=eol_product1.eol_product_id,
        version="20.04",
        release_date="2020-04-23",
        eol_from="2025-05-31",
        matching_version="ubuntu-20.04",
        created_at=now,
        updated_at=now,
    )
    persistence.create_eol_version(testdb, eol_version1)
    return eol_version1


@pytest.fixture(scope="function")
def eol_version2(
    testdb: Session,
    eol_product2: models.EoLProduct,
) -> models.EoLVersion:

    now = datetime.now(timezone.utc)
    eol_version2 = models.EoLVersion(
        eol_product_id=eol_product2.eol_product_id,
        version="3",
        release_date="2023-10-24",
        eol_from="2023-11-21",
        matching_version="3",
        created_at=now,
        updated_at=now,
    )
    persistence.create_eol_version(testdb, eol_version2)
    return eol_version2


class TestFixEoLDependencyByEoLProduct:
    def test_it_should_create_eol_dependency_when_ecosystem_matched(
        self,
        testdb: Session,
        service1: models.Service,
        eol_product1: models.EoLProduct,
        eol_version1: models.EoLVersion,
    ):
        # When
        eol_business.fix_eol_dependency_by_eol_product(testdb, eol_product1)

        # Then
        ecosystem_eol_dependency_1 = testdb.scalars(
            select(models.EcosystemEoLDependency).where(
                models.EcosystemEoLDependency.eol_version_id == str(eol_version1.eol_version_id)
            )
        ).one()

        assert ecosystem_eol_dependency_1.service.service_name == service1.service_name
        assert ecosystem_eol_dependency_1.eol_version.version == eol_version1.version
        assert (
            ecosystem_eol_dependency_1.eol_version.matching_version == eol_version1.matching_version
        )
        assert ecosystem_eol_dependency_1.eol_version.eol_product.name == eol_product1.name
        assert ecosystem_eol_dependency_1.eol_notification_sent is False

    def test_it_should_delete_eol_dependency_when_ecosystem_unmatched(
        self,
        testdb: Session,
        service1: models.Service,
        eol_product1: models.EoLProduct,
        eol_version1: models.EoLVersion,
    ):
        # Given
        eol_business.fix_eol_dependency_by_eol_product(testdb, eol_product1)
        eol_version1.matching_version = "unmatched_version"
        testdb.commit()

        # When
        eol_business.fix_eol_dependency_by_eol_product(testdb, eol_product1)

        # Then
        ecosystem_eol_dependency_1 = testdb.scalars(
            select(models.EcosystemEoLDependency).where(
                models.EcosystemEoLDependency.eol_version_id == str(eol_version1.eol_version_id)
            )
        ).one_or_none()

        assert ecosystem_eol_dependency_1 is None

    def test_it_should_create_eol_dependency_when_product_name_matched(
        self,
        testdb: Session,
        service2: models.Service,
        eol_product2: models.EoLProduct,
        eol_version2: models.EoLVersion,
    ):
        # When
        eol_business.fix_eol_dependency_by_eol_product(testdb, eol_product2)

        # Then
        package_eol_dependency_2 = testdb.scalars(
            select(models.PackageEoLDependency).where(
                models.PackageEoLDependency.eol_version_id == str(eol_version2.eol_version_id)
            )
        ).one()

        assert package_eol_dependency_2.dependency.service.service_name == service2.service_name
        assert package_eol_dependency_2.eol_version.version == eol_version2.version
        assert (
            package_eol_dependency_2.eol_version.matching_version == eol_version2.matching_version
        )
        assert package_eol_dependency_2.eol_version.eol_product.name == eol_product2.name
        assert package_eol_dependency_2.eol_notification_sent is False

    def test_it_should_delete_eol_dependency_when_package_name_unmatched(
        self,
        testdb: Session,
        service2: models.Service,
        eol_product2: models.EoLProduct,
        eol_version2: models.EoLVersion,
    ):
        # Given
        eol_business.fix_eol_dependency_by_eol_product(testdb, eol_product2)
        eol_version2.matching_version = "unmatched_version"
        testdb.commit()

        # When
        eol_business.fix_eol_dependency_by_eol_product(testdb, eol_product2)

        # Then
        package_eol_dependency_2 = testdb.scalars(
            select(models.PackageEoLDependency).where(
                models.PackageEoLDependency.eol_version_id == str(eol_version2.eol_version_id)
            )
        ).one_or_none()

        assert package_eol_dependency_2 is None


class TestFixEoLDependencyByService:
    def test_it_should_create_eol_dependency_when_ecosystem_matched(
        self,
        testdb: Session,
        service1: models.Service,
        eol_product1: models.EoLProduct,
        eol_version1: models.EoLVersion,
    ):
        # Given
        progress = TimeBasedProgressLogger(title="test")

        # When
        eol_business.fix_eol_dependency_by_service(testdb, service1, progress)

        # Then
        ecosystem_eol_dependency_1 = testdb.scalars(
            select(models.EcosystemEoLDependency).where(
                models.EcosystemEoLDependency.eol_version_id == str(eol_version1.eol_version_id)
            )
        ).one()

        assert ecosystem_eol_dependency_1.service.service_name == service1.service_name
        assert ecosystem_eol_dependency_1.eol_version.version == eol_version1.version
        assert (
            ecosystem_eol_dependency_1.eol_version.matching_version == eol_version1.matching_version
        )
        assert ecosystem_eol_dependency_1.eol_version.eol_product.name == eol_product1.name
        assert ecosystem_eol_dependency_1.eol_notification_sent is False

    def test_it_should_delete_eol_dependency_when_ecosystem_unmatched(
        self,
        testdb: Session,
        service1: models.Service,
        eol_product1: models.EoLProduct,
        eol_version1: models.EoLVersion,
    ):
        # Given
        progress = TimeBasedProgressLogger(title="test")
        eol_business.fix_eol_dependency_by_service(testdb, service1, progress)
        eol_version1.matching_version = "unmatched_version"
        testdb.commit()

        # When
        eol_business.fix_eol_dependency_by_service(testdb, service1, progress)

        # Then
        ecosystem_eol_dependency_1 = testdb.scalars(
            select(models.EcosystemEoLDependency).where(
                models.EcosystemEoLDependency.eol_version_id == str(eol_version1.eol_version_id)
            )
        ).one_or_none()

        assert ecosystem_eol_dependency_1 is None

    def test_it_should_create_eol_dependency_when_product_name_matched(
        self,
        testdb: Session,
        service2: models.Service,
        eol_product2: models.EoLProduct,
        eol_version2: models.EoLVersion,
    ):
        # Given
        progress = TimeBasedProgressLogger(title="test")

        # When
        eol_business.fix_eol_dependency_by_service(testdb, service2, progress)

        # Then
        package_eol_dependency_2 = testdb.scalars(
            select(models.PackageEoLDependency).where(
                models.PackageEoLDependency.eol_version_id == str(eol_version2.eol_version_id)
            )
        ).one()

        assert package_eol_dependency_2.dependency.service.service_name == service2.service_name
        assert package_eol_dependency_2.eol_version.version == eol_version2.version
        assert (
            package_eol_dependency_2.eol_version.matching_version == eol_version2.matching_version
        )
        assert package_eol_dependency_2.eol_version.eol_product.name == eol_product2.name
        assert package_eol_dependency_2.eol_notification_sent is False

    def test_it_should_delete_eol_dependency_when_package_name_unmatched(
        self,
        testdb: Session,
        service2: models.Service,
        eol_product2: models.EoLProduct,
        eol_version2: models.EoLVersion,
    ):
        # Given
        progress = TimeBasedProgressLogger(title="test")
        eol_business.fix_eol_dependency_by_service(testdb, service2, progress)
        eol_version2.matching_version = "unmatched_version"
        testdb.commit()

        # When
        eol_business.fix_eol_dependency_by_service(testdb, service2, progress)

        # Then
        package_eol_dependency_2 = testdb.scalars(
            select(models.PackageEoLDependency).where(
                models.PackageEoLDependency.eol_version_id == str(eol_version2.eol_version_id)
            )
        ).one_or_none()

        assert package_eol_dependency_2 is None


class TestEoLNotifications:
    """Test notification behavior when creating EoL dependencies"""

    def test_it_should_notify_on_ecosystem_eol_dependency_creation_by_eol_product(
        self,
        mocker,
        testdb: Session,
        service1: models.Service,
        eol_product1: models.EoLProduct,
        eol_version1: models.EoLVersion,
    ):
        pteam = service1.pteam
        pteam.alert_slack.enable = True
        pteam.alert_slack.webhook_url = "https://example.com/webhook"
        pteam.alert_mail.enable = True
        pteam.alert_mail.address = "account0@example.com"
        testdb.commit()

        eol_version1.eol_from = datetime.now(timezone.utc).date() + timedelta(
            days=EOL_WARNING_THRESHOLD_DAYS
        )
        testdb.commit()

        mocker.patch("app.notification.alert.ready_to_send_email", return_value=True)
        send_slack = mocker.patch("app.notification.alert.send_slack")
        send_email = mocker.patch("app.notification.alert.send_email")

        # When
        eol_business.fix_eol_dependency_by_eol_product(testdb, eol_product1)

        # Then
        assert send_slack.called
        assert send_email.called
        ecosystem_eol_dependency = testdb.scalars(
            select(models.EcosystemEoLDependency).where(
                models.EcosystemEoLDependency.eol_version_id == str(eol_version1.eol_version_id)
            )
        ).one()
        assert ecosystem_eol_dependency.eol_notification_sent is True

    def test_it_should_keep_notification_flag_false_when_notification_fails_ecosystem(
        self,
        mocker,
        testdb: Session,
        service1: models.Service,
        eol_product1: models.EoLProduct,
        eol_version1: models.EoLVersion,
    ):
        # Given
        mock_notify = mocker.patch("app.notification.alert.notify_eol_ecosystem")
        mock_notify.return_value = False

        # When
        eol_business.fix_eol_dependency_by_eol_product(testdb, eol_product1)

        # Then
        ecosystem_eol_dependency = testdb.scalars(
            select(models.EcosystemEoLDependency).where(
                models.EcosystemEoLDependency.eol_version_id == str(eol_version1.eol_version_id)
            )
        ).one()
        assert ecosystem_eol_dependency.eol_notification_sent is False

    def test_it_should_notify_on_package_eol_dependency_creation_by_eol_product(
        self,
        mocker,
        testdb: Session,
        service2: models.Service,
        eol_product2: models.EoLProduct,
        eol_version2: models.EoLVersion,
    ):
        # Given
        pteam = service2.pteam
        pteam.alert_slack.enable = True
        pteam.alert_slack.webhook_url = "https://example.com/webhook"
        pteam.alert_mail.enable = True
        pteam.alert_mail.address = "account0@example.com"
        testdb.commit()

        eol_version2.eol_from = datetime.now(timezone.utc).date() + timedelta(
            days=EOL_WARNING_THRESHOLD_DAYS
        )
        testdb.commit()

        mocker.patch("app.notification.alert.ready_to_send_email", return_value=True)
        send_slack = mocker.patch("app.notification.alert.send_slack")
        send_email = mocker.patch("app.notification.alert.send_email")

        # When
        eol_business.fix_eol_dependency_by_eol_product(testdb, eol_product2)

        # Then
        assert send_slack.called
        assert send_email.called
        package_eol_dependency = testdb.scalars(
            select(models.PackageEoLDependency).where(
                models.PackageEoLDependency.eol_version_id == str(eol_version2.eol_version_id)
            )
        ).one()
        assert package_eol_dependency.eol_notification_sent is True

    def test_it_should_keep_notification_flag_false_when_notification_fails_package(
        self,
        mocker,
        testdb: Session,
        service2: models.Service,
        eol_product2: models.EoLProduct,
        eol_version2: models.EoLVersion,
    ):
        # Given
        mock_notify = mocker.patch("app.notification.alert.notify_eol_package")
        mock_notify.return_value = False

        # When
        eol_business.fix_eol_dependency_by_eol_product(testdb, eol_product2)

        # Then
        package_eol_dependency = testdb.scalars(
            select(models.PackageEoLDependency).where(
                models.PackageEoLDependency.eol_version_id == str(eol_version2.eol_version_id)
            )
        ).one()
        assert package_eol_dependency.eol_notification_sent is False

    def test_it_should_notify_on_ecosystem_eol_dependency_creation_by_service(
        self,
        mocker,
        testdb: Session,
        service1: models.Service,
        eol_product1: models.EoLProduct,
        eol_version1: models.EoLVersion,
    ):
        # Given
        pteam = service1.pteam
        pteam.alert_slack.enable = True
        pteam.alert_slack.webhook_url = "https://example.com/webhook"
        pteam.alert_mail.enable = True
        pteam.alert_mail.address = "account0@example.com"
        testdb.commit()

        eol_version1.eol_from = datetime.now(timezone.utc).date() + timedelta(
            days=EOL_WARNING_THRESHOLD_DAYS
        )
        testdb.commit()

        mocker.patch("app.notification.alert.ready_to_send_email", return_value=True)
        send_slack = mocker.patch("app.notification.alert.send_slack")
        send_email = mocker.patch("app.notification.alert.send_email")

        progress = TimeBasedProgressLogger(title="test")

        # When
        eol_business.fix_eol_dependency_by_service(testdb, service1, progress)

        # Then
        assert send_slack.called
        assert send_email.called
        ecosystem_eol_dependency = testdb.scalars(
            select(models.EcosystemEoLDependency).where(
                models.EcosystemEoLDependency.eol_version_id == str(eol_version1.eol_version_id)
            )
        ).one()
        assert ecosystem_eol_dependency.eol_notification_sent is True

    def test_it_should_notify_on_package_eol_dependency_creation_by_service(
        self,
        mocker,
        testdb: Session,
        service2: models.Service,
        eol_product2: models.EoLProduct,
        eol_version2: models.EoLVersion,
    ):
        # Given
        pteam = service2.pteam
        pteam.alert_slack.enable = True
        pteam.alert_slack.webhook_url = "https://example.com/webhook"
        pteam.alert_mail.enable = True
        pteam.alert_mail.address = "account0@example.com"
        testdb.commit()

        eol_version2.eol_from = datetime.now(timezone.utc).date() + timedelta(
            days=EOL_WARNING_THRESHOLD_DAYS
        )
        testdb.commit()

        mocker.patch("app.notification.alert.ready_to_send_email", return_value=True)
        send_slack = mocker.patch("app.notification.alert.send_slack")
        send_email = mocker.patch("app.notification.alert.send_email")

        progress = TimeBasedProgressLogger(title="test")

        # When
        eol_business.fix_eol_dependency_by_service(testdb, service2, progress)

        # Then
        assert send_slack.called
        assert send_email.called
        package_eol_dependency = testdb.scalars(
            select(models.PackageEoLDependency).where(
                models.PackageEoLDependency.eol_version_id == str(eol_version2.eol_version_id)
            )
        ).one()
        assert package_eol_dependency.eol_notification_sent is True

    def test_it_should_not_notify_when_ecosystem_eol_dependency_already_exists(
        self,
        mocker,
        testdb: Session,
        service1: models.Service,
        eol_product1: models.EoLProduct,
        eol_version1: models.EoLVersion,
    ):
        # Given
        mock_notify = mocker.patch("app.notification.alert.notify_eol_ecosystem")
        eol_business.fix_eol_dependency_by_eol_product(testdb, eol_product1)
        mock_notify.reset_mock()

        # When
        eol_business.fix_eol_dependency_by_eol_product(testdb, eol_product1)

        # Then
        mock_notify.assert_not_called()

    def test_it_should_not_notify_when_package_eol_dependency_already_exists(
        self,
        mocker,
        testdb: Session,
        service1: models.Service,
        eol_product2: models.EoLProduct,
        eol_version2: models.EoLVersion,
    ):
        # Given
        mock_notify = mocker.patch("app.notification.alert.notify_eol_package")
        eol_business.fix_eol_dependency_by_eol_product(testdb, eol_product2)
        mock_notify.reset_mock()

        # When
        eol_business.fix_eol_dependency_by_eol_product(testdb, eol_product2)

        # Then
        mock_notify.assert_not_called()

    def test_it_should_alert_immediately_when_ecosystem_eol_within_six_months_on_creation(
        self,
        mocker,
        testdb: Session,
        service1: models.Service,
        eol_product1: models.EoLProduct,
        eol_version1: models.EoLVersion,
    ):
        pteam = service1.pteam
        pteam.alert_slack.enable = True
        pteam.alert_slack.webhook_url = "https://example.com/webhook"
        pteam.alert_mail.enable = True
        pteam.alert_mail.address = "account0@example.com"
        testdb.commit()

        eol_version1.eol_from = datetime.now(timezone.utc).date() + timedelta(
            days=EOL_WARNING_THRESHOLD_DAYS
        )
        testdb.commit()

        mocker.patch("app.notification.alert.ready_to_send_email", return_value=True)
        send_slack = mocker.patch("app.notification.alert.send_slack")
        send_email = mocker.patch("app.notification.alert.send_email")

        progress = TimeBasedProgressLogger(title="test")
        eol_business.fix_eol_dependency_by_service(testdb, service1, progress)

        assert send_slack.called
        assert send_email.called

        ecosystem_eol_dependency = testdb.scalars(
            select(models.EcosystemEoLDependency).where(
                models.EcosystemEoLDependency.eol_version_id == str(eol_version1.eol_version_id),
                models.EcosystemEoLDependency.service_id == str(service1.service_id),
            )
        ).one()
        assert ecosystem_eol_dependency.eol_notification_sent is True

    def test_it_should_not_alert_immediately_when_ecosystem_eol_beyond_six_months_on_creation(
        self,
        mocker,
        testdb: Session,
        service1: models.Service,
        eol_product1: models.EoLProduct,
        eol_version1: models.EoLVersion,
    ):
        from datetime import datetime, timedelta, timezone

        from sqlalchemy import select

        pteam = service1.pteam
        pteam.alert_slack.enable = True
        pteam.alert_slack.webhook_url = "https://example.com/webhook"
        pteam.alert_mail.enable = True
        pteam.alert_mail.address = "account0@example.com"
        testdb.commit()

        eol_version1.eol_from = datetime.now(timezone.utc).date() + timedelta(
            days=EOL_WARNING_THRESHOLD_DAYS + 1
        )
        testdb.commit()

        mocker.patch("app.notification.alert.ready_to_send_email", return_value=True)
        send_slack = mocker.patch("app.notification.alert.send_slack")
        send_email = mocker.patch("app.notification.alert.send_email")

        progress = TimeBasedProgressLogger(title="test")
        eol_business.fix_eol_dependency_by_service(testdb, service1, progress)

        assert not send_slack.called
        assert not send_email.called

        ecosystem_eol_dependency = testdb.scalars(
            select(models.EcosystemEoLDependency).where(
                models.EcosystemEoLDependency.eol_version_id == str(eol_version1.eol_version_id),
                models.EcosystemEoLDependency.service_id == str(service1.service_id),
            )
        ).one()
        assert ecosystem_eol_dependency.eol_notification_sent is False

    def test_it_should_alert_immediately_when_package_eol_within_six_months_on_creation(
        self,
        mocker,
        testdb: Session,
        service2: models.Service,
        eol_product2: models.EoLProduct,
        eol_version2: models.EoLVersion,
    ):
        pteam = service2.pteam
        pteam.alert_slack.enable = True
        pteam.alert_slack.webhook_url = "https://example.com/webhook"
        pteam.alert_mail.enable = True
        pteam.alert_mail.address = "account0@example.com"
        testdb.commit()

        eol_version2.eol_from = datetime.now(timezone.utc).date() + timedelta(
            days=EOL_WARNING_THRESHOLD_DAYS
        )
        testdb.commit()

        mocker.patch("app.notification.alert.ready_to_send_email", return_value=True)
        send_slack = mocker.patch("app.notification.alert.send_slack")
        send_email = mocker.patch("app.notification.alert.send_email")

        progress = TimeBasedProgressLogger(title="test")
        eol_business.fix_eol_dependency_by_service(testdb, service2, progress)

        assert send_slack.called
        assert send_email.called

        package_eol_dependency = testdb.scalars(
            select(models.PackageEoLDependency).where(
                models.PackageEoLDependency.eol_version_id == str(eol_version2.eol_version_id)
            )
        ).one()
        assert package_eol_dependency.eol_notification_sent is True

    def test_it_should_not_alert_immediately_when_package_eol_beyond_six_months_on_creation(
        self,
        mocker,
        testdb: Session,
        service2: models.Service,
        eol_product2: models.EoLProduct,
        eol_version2: models.EoLVersion,
    ):
        from datetime import datetime, timedelta, timezone

        from sqlalchemy import select

        pteam = service2.pteam
        pteam.alert_slack.enable = True
        pteam.alert_slack.webhook_url = "https://example.com/webhook"
        pteam.alert_mail.enable = True
        pteam.alert_mail.address = "account0@example.com"
        testdb.commit()

        eol_version2.eol_from = datetime.now(timezone.utc).date() + timedelta(
            days=EOL_WARNING_THRESHOLD_DAYS + 1
        )
        testdb.commit()

        mocker.patch("app.notification.alert.ready_to_send_email", return_value=True)
        send_slack = mocker.patch("app.notification.alert.send_slack")
        send_email = mocker.patch("app.notification.alert.send_email")

        progress = TimeBasedProgressLogger(title="test")
        eol_business.fix_eol_dependency_by_service(testdb, service2, progress)

        assert not send_slack.called
        assert not send_email.called

        package_eol_dependency = testdb.scalars(
            select(models.PackageEoLDependency).where(
                models.PackageEoLDependency.eol_version_id == str(eol_version2.eol_version_id)
            )
        ).one()
        assert package_eol_dependency.eol_notification_sent is False
