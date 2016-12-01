from tinker_access_client.ClientLogger import ClientLogger

LCD_LINE_1 = 0
LCD_LINE_2 = 1


logger = ClientLogger.setup()


def lcd_init():
    pass


def lcd_string(message, _):
    logger.info('\033[1mLCD-OUTPUT: %s\033[0m', message)
