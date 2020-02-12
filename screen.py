import I2C_LCD_driver
import time

mylcd = I2C_LCD_driver.lcd()

mylcd.lcd_display_string(str(time.localtime()[3]) + ":" + str(time.localtime()[4]), 1)
mylcd.lcd_display_string_pos(str())