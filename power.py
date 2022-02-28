import logging
import subprocess

from datetime import datetime

logger = logging.getLogger(__name__)

class PowerHelper:
    def get_battery(self) -> float:
        battery_float = -1
        try:
            ps = subprocess.Popen(('echo', 'get battery'), stdout=subprocess.PIPE)
            result = subprocess.check_output(('nc', '-q', '0', '127.0.0.1', '8423'), stdin=ps.stdout)
            ps.wait()
            result_str = result.decode('utf-8').rstrip()
            battery_level = result_str.split()[-1]
            battery_float = float(battery_level)
        except (ValueError, subprocess.CalledProcessError) as e:
            logger.error(f'Invalid battery output: {result_str}. Likely on dedicated power.')
        return battery_float

    def set_next_boot_datetime(self, boot_time) -> None:
        try:
            formatted_boot_time = boot_time.astimezone().isoformat()
            ps = subprocess.Popen(('echo', f'rtc_alarm_set {formatted_boot_time} 127'), stdout=subprocess.PIPE)
            result = subprocess.check_output(('nc', '-q', '0', '127.0.0.1', '8423'), stdin=ps.stdout)
            ps.wait()
            result_str = result.decode('utf-8').rstrip()
            if(result_str == 'rtc_alarm_set: done'):
                logger.info(f"Successfully set next boot time to {formatted_boot_time}")
            else:
                logger.error(f'Error setting next boot time to {formatted_boot_time}: {result_str}')
        except (ValueError, subprocess.CalledProcessError) as e:
            logger.error(f'Error setting next boot time to {boot_time}')
