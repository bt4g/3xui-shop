import logging

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsAdmin
from app.bot.utils.constants import MAIN_MESSAGE_ID_KEY
from app.bot.utils.navigation import NavMain
from app.db.models import User

from .keyboard import main_menu_keyboard

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.message(Command(NavMain.START))
async def command_main_menu(message: Message, user: User, state: FSMContext) -> None:
    logger.info(f"User {user.tg_id} opened main menu page.")
    previous_message_id = await state.get_value(MAIN_MESSAGE_ID_KEY)

    if previous_message_id:
        try:
            await message.bot.delete_message(chat_id=user.tg_id, message_id=previous_message_id)
            logger.debug(f"Main message for user {user.tg_id} deleted.")
        except Exception as exception:
            logger.error(f"Failed to delete main message for user {user.tg_id}: {exception}")
        finally:
            await state.clear()

    is_admin = await IsAdmin()(user_id=user.tg_id)
    main_menu = await message.answer(
        text=_("main_menu:message:main").format(name=user.first_name),
        reply_markup=main_menu_keyboard(is_admin),
    )
    await state.update_data({MAIN_MESSAGE_ID_KEY: main_menu.message_id})


@router.callback_query(F.data == NavMain.MAIN_MENU)
async def callback_main_menu(callback: CallbackQuery, user: User, state: FSMContext) -> None:
    logger.info(f"User {user.tg_id} returned to main menu page.")
    await state.clear()
    await state.update_data({MAIN_MESSAGE_ID_KEY: callback.message.message_id})
    is_admin = await IsAdmin()(user_id=user.tg_id)
    await callback.message.edit_text(
        text=_("main_menu:message:main").format(name=user.first_name),
        reply_markup=main_menu_keyboard(is_admin),
    )


async def redirect_to_main_menu(
    bot: Bot,
    user: User,
    storage: RedisStorage | None = None,
    state: FSMContext | None = None,
) -> None:
    logger.info(f"User {user.tg_id} redirected to main menu page.")

    if not state:
        state: FSMContext = FSMContext(
            storage=storage,
            key=StorageKey(bot_id=bot.id, chat_id=user.tg_id, user_id=user.tg_id),
        )

    main_message_id = await state.get_value(MAIN_MESSAGE_ID_KEY)
    is_admin = await IsAdmin()(user_id=user.tg_id)

    await bot.edit_message_text(
        text=_("main_menu:message:main").format(name=user.first_name),
        chat_id=user.tg_id,
        message_id=main_message_id,
        reply_markup=main_menu_keyboard(is_admin),
    )
