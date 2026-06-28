"""File in charge of data encryption"""
import bcrypt
import hmac
import hashlib
from typing import Any,Optional
from loguru import logger

class PepperAvancedDinamycs(object):
    """Advanced class to encrypt user password"""
    def __init__(self,rounds:int = 3):
        self.master_pepper = "Val220117" #Este sera un secreto (Secrets Manager).
        self.rounds = rounds

    def _generate_pepper_user(self,username:str,email:Optional[str]=None) -> str:
        """
        function to generate the user pepper
        factor_extra: Could be email,fecha_registry,etc
        """
        try:
            #1.- Base: master_pepper + username
            base = username

            #2.- Add extra factor if it exists.
            if email:
                base = base + email

            #3.- Use HMAC for added security.
            return hmac.new(
                self.master_pepper.encode('utf-8'),
                base.encode('utf-8'),
                hashlib.sha3_512
            ).digest()
        except Exception as error:
            logger.error(f"Error in _generate_pepper_user : {error}")

    def _apply_pepper_multiple(self,password:str,pepper:str) -> str:
        """Apply the pepper multiple times for added safety"""
        try:
            password_bytes = password.encode('utf-8')
            
            #1.- Apply pepper multiple times.
            for i in range(self.rounds):
                if i % 2 == 0:
                    password_bytes = password_bytes + pepper
                else:
                    password_bytes = pepper + password_bytes
                    
            return hashlib.sha512(password_bytes).digest()
        except Exception as error:
            logger.error(f"Error in _apply_pepper_multiple : {error}")

    def _register_user(self,username:str,password:str,email:Optional[str] = None) -> dict[str,Any]:
        """Registration with additional factors"""
        try:
            #1.- Generate pepper with factors.
            pepper_user = self._generate_pepper_user(username,email)
            
            #2.-Apply pepper multiples times.
            password_procesed = self._apply_pepper_multiple(password,pepper_user)
            
            #3.- Hash with bcrypt.
            hashed = bcrypt.hashpw(
                password_procesed,
                bcrypt.gensalt(rounds=12)
            )
            
            return hashed.decode('utf-8')
        except Exception as error:
            logger.error(f"Error in _register_user : {error}")

    def _verify_login(self,username:str,password:str,hash_saved:str,email:Optional[str]=None):
        """Verification regenerating the pepper with the same factors"""
        try:
            #1.- Regenerate pepper with the same factors.
            pepper_user = self._generate_pepper_user(username,email)
            
            #Apply pepper in the same way.
            password_procesed = self._apply_pepper_multiple(password,pepper_user)
            
            return bcrypt.checkpw(
                password_procesed,
                hash_saved.encode('utf-8')
            )
        except Exception as error:
            logger.error(f"Error in _verify_login : {error}")

""" 
if __name__ == '__main__':
    encriptar = PepperAvancedDinamycs()
    data = encriptar._register_user(
        username="Juanv220117",
        password="Val220117",
        email="juan@vexi.mx"
    )
    logger.debug(data)
    #Validar_contraseña
    logger.warning(
        encriptar._verify_login(
            username="Juanv220117",
            password="Val220117",
            hash_saved=data.get("password_hash"),
            email="juan@vexi.mx"
        )
        )
    
    
"""
