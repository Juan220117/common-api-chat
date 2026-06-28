"""Class with user table logic"""
from typing import Any
#Repositories
from repositories.UsersRepository import UsersRepository
from repositories.UsersInfoRepository import UserInformationRepository
#Models
from models.UsersModel import UsersModel
from models.UsersInfoModel import UsersInformationModel
#Utils
from utils.encript import PepperAvancedDinamycs
from loguru import logger

class UserService(object):
    """Business class"""
    
    def __init__(self,uow):
        self.uow = uow
        self.user_repository = UsersRepository(uow.session)
        self.informacion_repository = UserInformationRepository(uow.session)

    def create_user(self,username:str,password:str,email:str,personal_information:dict[str,Any]) -> dict[str,Any]:
        """Funcion para crear usuario"""
        try:
            #1.- Validate username availability.
            coincidence= self.user_repository.get_user_by_user_name_or_email(username,email)
            if coincidence:
                return coincidence

            #2.-Generate encrypted password
            password_hashed = PepperAvancedDinamycs()._register_user(
                username=username,
                password=password,
                email=email
            )
            
            #3.- Generate user.
            new_user = UsersModel(
                username=username,
                password=password_hashed,
                email=email
            )
            self.user_repository.create_user(new_user=new_user)
            
            #2.-Save personal information.
            new_user_information = UsersInformationModel(**personal_information)
            new_user_information.id_user = new_user.id_user
            self.informacion_repository.save_personal_information(data=new_user_information)

            self.uow.commit()
            return new_user
        except Exception as error:
            logger.error(f"Error en create user : {error}")
    
    def login_user(self,username:str,password:str) -> bool:
        try:
            #1.-Get database record.
            record = self.user_repository.get_user_by_username(username=username)
            if not record:
                return f"User {username} not found"
            
            #2.- Validate password
            validate = PepperAvancedDinamycs()._verify_login(
                username=username,
                password=password,
                hash_saved=record.password,
                email=record.email
            )
            if not validate:
                return f"User {username} incorrect password"
            
            return True
        except Exception as error:
            logger.error(f"Erro in login_user : {error}")
