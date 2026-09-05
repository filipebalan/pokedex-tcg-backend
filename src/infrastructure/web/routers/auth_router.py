from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.session import get_db_session
from src.infrastructure.database.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from src.infrastructure.security.password_service import PasswordService
from src.infrastructure.security.token_service import TokenService
from src.application.use_cases.register_user_use_case import RegisterUserUseCase
from src.application.use_cases.authenticate_user_use_case import AuthenticateUserUseCase
from src.infrastructure.web.dtos.auth_dtos import RegisterUserRequestDTO, UserResponseDTO, TokenResponseDTO
from src.infrastructure.web.middlewares.rate_limiter import RateLimiter

router = APIRouter(prefix="/auth", tags=["Auth"])
rate_limiter = RateLimiter(requests_per_minute=20)  # Limite defensivo para rotas de login

password_service = PasswordService()
token_service = TokenService()

@router.post(
    "/register",
    response_model=UserResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar novo usuário",
    dependencies=[Depends(rate_limiter)]
)
async def register(
    payload: RegisterUserRequestDTO,
    session: AsyncSession = Depends(get_db_session)
) -> UserResponseDTO:
    user_repo = SQLAlchemyUserRepository(session)
    use_case = RegisterUserUseCase(user_repo, password_service)

    try:
        user = await use_case.execute(payload.email, payload.password)
        await session.commit()
        return UserResponseDTO(id=user.id, email=user.email, created_at=user.created_at)
    except ValueError as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.post(
    "/login",
    response_model=TokenResponseDTO,
    summary="Autenticar usuário e obter token JWT",
    dependencies=[Depends(rate_limiter)]
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db_session)
) -> TokenResponseDTO:
    # O padrão OAuth2PasswordRequestForm usa o campo 'username' para receber o email
    user_repo = SQLAlchemyUserRepository(session)
    use_case = AuthenticateUserUseCase(user_repo, password_service, token_service)

    token = await use_case.execute(form_data.username, form_data.password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return TokenResponseDTO(access_token=token)