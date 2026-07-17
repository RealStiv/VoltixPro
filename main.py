    if dato == "verificar_sus":
        await query.answer()  # ✅ OBLIGATORIO, YA LO TIENES PUESTO
        if await verificar_suscripcion(update, context):
            await query.edit_message_text(t("suscrito_correcto"), parse_mode="HTML")
            await inicio(update, context)
        else:
            await query.answer("❌ Aún no apareces como suscrito. Espera 1 minuto y vuelve a pulsar", show_alert=True)
