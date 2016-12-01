from mock import Mock


class LCD(Mock):
    LCD_LINE_1 = 0
    LCD_LINE_2 = 1


class MockLcd:
    LCD = LCD()

