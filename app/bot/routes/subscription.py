import json
import logging

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.bot.filters.is_private import IsPrivate
from app.bot.keyboards.payment_method import payment_method_keyboard
from app.bot.keyboards.subscription import duration_keyboard, traffic_keyboard
from app.bot.navigation import NavigationAction
from app.bot.services.subscription import SubscriptionService

logger = logging.getLogger(__name__)
router = Router(name=__name__)


async def show_choosing_traffic(
    callback: CallbackQuery,
    subscription: SubscriptionService,
) -> None:
    """
    Prompts the user to select the traffic volume for their subscription.

    Arguments:
        callback (CallbackQuery): The callback query from the user.
        subscription (SubscriptionService): The subscription service instance.
    """
    text = _("🌐 Select the traffic volume:")
    await callback.message.answer(text, reply_markup=traffic_keyboard(subscription))


async def show_choosing_duration(
    callback: CallbackQuery,
    state: FSMContext,
    subscription: SubscriptionService,
) -> None:
    """
    Sends a message prompting the user to select the subscription duration based on their plan.

    Arguments:
        callback (CallbackQuery): The callback query from the user.
        state (FSMContext): The user's FSM state.
        subscription (SubscriptionService): The subscription service instance.
    """
    plan_callback = await state.get_value("plan_callback")
    plan = subscription.get_plan(plan_callback)
    await callback.message.answer(
        _("⏳ Specify the duration:"),
        reply_markup=duration_keyboard(plan["prices"], subscription),
    )


async def show_choosing_payment_method(
    callback: CallbackQuery,
    state: FSMContext,
    subscription: SubscriptionService,
) -> None:
    """
    Sends a message prompting the user to choose a payment method for their subscription.

    Arguments:
        callback (CallbackQuery): The callback query from the user.
        state (FSMContext): The user's FSM state.
        subscription (SubscriptionService): The subscription service instance.
    """
    plan_callback = await state.get_value("plan_callback")
    duration_callback = await state.get_value("duration_callback")
    plan = subscription.get_plan(plan_callback)
    duration = subscription.get_duration(duration_callback)
    await callback.message.answer(
        _("💳 Choose a payment method:"),
        reply_markup=payment_method_keyboard(plan["prices"], duration, subscription),
    )


@router.callback_query(F.data == NavigationAction.SUBSCRIPTION, IsPrivate())
async def callback_subscription(
    callback: CallbackQuery,
    subscription: SubscriptionService,
) -> None:
    """
    Handles the subscription initiation by sending the traffic selection prompt.

    Arguments:
        callback (CallbackQuery): The callback query from the user.
        subscription (SubscriptionService): The subscription service instance.
    """
    logger.info(f"User {callback.from_user.id} started subscription process.")
    await callback.message.delete()
    await show_choosing_traffic(callback, subscription)


@router.callback_query(F.data.startswith(NavigationAction.TRAFFIC), IsPrivate())
async def callback_choosing_plan(
    callback: CallbackQuery,
    state: FSMContext,
    subscription: SubscriptionService,
) -> None:
    """
    Handles traffic plan selection and proceeds to duration selection.

    Arguments:
        callback (CallbackQuery): The callback query from the user.
        state (FSMContext): The user's FSM state.
        subscription (SubscriptionService): The subscription service instance.
    """
    await callback.message.delete()
    logger.info(f"User {callback.from_user.id} selected plan: {callback.data}")
    await state.update_data(plan_callback=callback.data)
    await show_choosing_duration(callback, state, subscription)


@router.callback_query(F.data == NavigationAction.BACK_TO_DURATION, IsPrivate())
async def callback_back_to_duration(
    callback: CallbackQuery,
    state: FSMContext,
    subscription: SubscriptionService,
) -> None:
    """
    Handles the user returning to the duration selection step.

    Arguments:
        callback (CallbackQuery): The callback query from the user.
        state (FSMContext): The user's FSM state.
        subscription (SubscriptionService): The subscription service instance.
    """
    await callback.message.delete()
    logger.info(f"User {callback.from_user.id} returned to choosing duration.")
    await show_choosing_duration(callback, state, subscription)


@router.callback_query(F.data.startswith(NavigationAction.DURATION), IsPrivate())
async def callback_choosing_duration(
    callback: CallbackQuery,
    state: FSMContext,
    subscription: SubscriptionService,
) -> None:
    """
    Handles duration selection and proceeds to payment method selection.

    Arguments:
        callback (CallbackQuery): The callback query from the user.
        state (FSMContext): The user's FSM state.
        subscription (SubscriptionService): The subscription service instance.
    """
    await callback.message.delete()
    logger.info(f"User {callback.from_user.id} selected duration: {callback.data}")
    await state.update_data(duration_callback=callback.data)
    await show_choosing_payment_method(callback, state, subscription)


@router.callback_query(F.data == NavigationAction.BACK_TO_PAYMENT, IsPrivate())
async def callback_back_to_payment(
    callback: CallbackQuery,
    state: FSMContext,
    subscription: SubscriptionService,
) -> None:
    """
    Handles the user returning to the payment method selection step.

    Arguments:
        callback (CallbackQuery): The callback query from the user.
        state (FSMContext): The user's FSM state.
        subscription (SubscriptionService): The subscription service instance.
    """
    await callback.message.delete()
    logger.info(f"User {callback.from_user.id} returned to choosing payment method.")
    await show_choosing_payment_method(callback, state, subscription)
