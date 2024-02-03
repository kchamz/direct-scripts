from http import HTTPStatus
from typing import Optional, List

import requests

from schemas.api_schemas.proposal_create.proposal_create import ProposalCreate
from schemas.api_schemas.proposal_item_create.proposal_item_create import (
    ProposalProposalItemCreate,
    ProposalItemCreate,
)
from exceptions.exceptions import (
    UserLoginException,
    ProposalCreateException,
    EmbeddingException,
    ProposalItemGetException,
    ProposalGetException,
)
from schemas.schemas import SessionUserData, LoginInfo


class DirectClient:
    session_user_data: Optional[SessionUserData] = None

    def __init__(self, base_url: str, login_info: LoginInfo) -> None:
        self._base_url = base_url
        self._login_info = login_info

    def login(self) -> None:
        login_url = f"{self._base_url}/login"

        response = requests.post(
            url=login_url, data=self._login_info.to_dict(), verify=False
        )

        if response.status_code == HTTPStatus.UNAUTHORIZED:
            raise UserLoginException("Unauthorized login.")

        self.session_user_data = SessionUserData(
            id=response.json()["user"]["id"],
            email=response.json()["user"]["email"],
            cookies=response.cookies,
        )

        print("Login successful.")

    def create_proposal(self, data: ProposalCreate = ProposalCreate()) -> int:
        proposal_create_url = f"{self._base_url}/api/v1/proposal"

        if not data.owner_email:
            data.owner_email = self.session_user_data.email
        if not data.owner_user_id:
            data.owner_user_id = self.session_user_data.id

        response = requests.post(
            url=proposal_create_url,
            data=data.json(),
            cookies=self.session_user_data.cookies,
            verify=False,
        )

        if response.status_code != HTTPStatus.CREATED:
            raise ProposalCreateException(
                f"Error creating proposal: {str(response.text)}"
            )

        return response.json()["id"]

    def create_proposal_items(
        self,
        data: ProposalProposalItemCreate = ProposalProposalItemCreate(),
        number_of_plis: int = 1,
    ) -> List[int]:
        proposal_items_create_url = f"{self._base_url}/api/v1/proposal/proposal_items"

        if data.proposal_id is None:
            data.proposal_id = self.create_proposal()

        if data.line_items is None:
            data.line_items = [ProposalItemCreate()] * number_of_plis

        response = requests.post(
            url=proposal_items_create_url,
            data=data.json(),
            cookies=self.session_user_data.cookies,
            verify=False,
        )

        if response.status_code != HTTPStatus.CREATED:
            raise ProposalCreateException(
                f"Error creating proposal: {str(response.text)}"
            )

        return [pli["id"] for pli in response.json()["line_items"]]

    def generate_embedded_url(
        self, redirect_url: str, login_as_email: Optional[str] = None
    ):
        if login_as_email is None:
            login_as_email = self.session_user_data.email

        embedded_url = f"{self._base_url}/api/v1/embedded/generate?redirect={redirect_url}&login_as_email={login_as_email}"

        response = requests.get(
            url=embedded_url,
            cookies=self.session_user_data.cookies,
            verify=False,
        )

        if response.status_code != HTTPStatus.OK:
            raise EmbeddingException(f"Error embedding: {redirect_url}")

        return response.json()["embedded_url"]

    def get_proposal_item(self, proposal_item_id: int) -> dict:
        get_pli_url = (
            f"{self._base_url}/api/v1/proposal/proposal_item/{proposal_item_id}"
        )

        response = requests.get(
            url=get_pli_url,
            cookies=self.session_user_data.cookies,
            verify=False,
        )

        if response.status_code != HTTPStatus.OK:
            raise ProposalItemGetException(
                f"Error fetching proposal item {proposal_item_id}"
            )

        return response.json()

    def get_proposal(self, proposal_id: int) -> dict:
        get_proposal_url = f"{self._base_url}/api/v1/proposal/{proposal_id}"

        response = requests.get(
            url=get_proposal_url,
            cookies=self.session_user_data.cookies,
            verify=False,
        )

        if response.status_code != HTTPStatus.OK:
            raise ProposalGetException(f"Error fetching proposal {proposal_id}")

        return response.json()

    def get_domain_id_from_proposal_item_id(
        self, proposal_item_id: int
    ) -> Optional[int]:
        proposal_item = self.get_proposal_item(proposal_item_id=proposal_item_id)

        proposal_id = proposal_item["proposal_id"]

        proposal = self.get_proposal(proposal_id=proposal_id)

        domain_id = proposal["domain_id"]

        return int(domain_id)
