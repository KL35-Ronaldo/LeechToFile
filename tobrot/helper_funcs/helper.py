import os
import time
import math
import shutil
import asyncio
import logging
from pyrogram import filters
from tobrot import FINISHED_PROGRESS_STR, UN_FINISHED_PROGRESS_STR


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
LOGGER = logging.getLogger(__name__)


async def is_admin(f, c, m):
    user = await c.get_chat_member(m.chat.id, m.from_user.id)
    return bool(user.status in ["creator", "administrator"])
admins = filters.create(is_admin)


async def copy_file(input_file, output_dir):
    output_file = os.path.join(
        output_dir,
        str(time.time()) + ".jpg"
    )
    shutil.copyfile(input_file, output_file)
    return output_file


async def create_archive(input_directory):
    return_name = None
    if os.path.exists(input_directory):
        base_dir_name = os.path.basename(input_directory)
        compressed_file_name = f"{base_dir_name}.tar.gz"
        suffix_extention_length = 1 + 3 + 1 + 2
        if len(base_dir_name) > (64 - suffix_extention_length):
            compressed_file_name = base_dir_name[0:(64 - suffix_extention_length)]
            compressed_file_name += ".tar.gz"
        file_genertor_command = [
            "tar",
            "-zcvf",
            compressed_file_name,
            f"{input_directory}"
        ]
        process = await asyncio.create_subprocess_exec(
            *file_genertor_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        e_response = stderr.decode().strip()
        t_response = stdout.decode().strip()
        if os.path.exists(compressed_file_name):
            try:
                shutil.rmtree(input_directory)
            except:
                pass
            return_name = compressed_file_name
    return return_name


async def unzip_me(input_directory):
    return_name = None
    if os.path.exists(input_directory):
        base_dir_name = os.path.basename(input_directory)
        uncompressed_file_name = os.path.splitext(base_dir_name)[0]
        g_cmd = ["unzip", "-o", f"{base_dir_name}", "-d", f"{uncompressed_file_name}"]
        ga_utam = await asyncio.create_subprocess_exec(*g_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        gau, tam = await ga_utam.communicate()
        LOGGER.info(gau)
        LOGGER.info(tam)
        if os.path.exists(uncompressed_file_name):
            try:
                os.remove(input_directory)
            except:
                pass
            return_name = uncompressed_file_name
            print(return_name)
    return return_name


async def untar_me(input_directory):
    return_name = None
    if os.path.exists(input_directory):
        print(input_directory)
        base_dir_name = os.path.basename(input_directory)
        uncompressed_file_name = os.path.splitext(base_dir_name)[0]
        m_k_gaut = ['mkdir', f'{uncompressed_file_name}']
        await asyncio.create_subprocess_exec(*m_k_gaut, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        g_cmd_t = ["tar", "-xvf", f"/app/{base_dir_name}", "-C", f"{uncompressed_file_name}"]
        bc_kanger = await asyncio.create_subprocess_exec(*g_cmd_t, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        mc, kanger = await bc_kanger.communicate()
        LOGGER.info(mc)
        LOGGER.info(kanger)
        if os.path.exists(uncompressed_file_name):
            try:
                os.remove(input_directory)
            except:
                pass
            return_name = uncompressed_file_name
            LOGGER.info(return_name)
    return return_name


async def unrar_me(input_directory):
    return_name = None
    if os.path.exists(input_directory):
        base_dir_name = os.path.basename(input_directory)
        uncompressed_file_name = os.path.splitext(base_dir_name)[0]
        m_k_gau = ['mkdir', f'{uncompressed_file_name}']
        await asyncio.create_subprocess_exec(*m_k_gau, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        print(base_dir_name)
        gau_tam_r = ["unrar", "x", f"{base_dir_name}", f"{uncompressed_file_name}"]
        jai_hind = await asyncio.create_subprocess_exec(*gau_tam_r, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        jai, hind = await jai_hind.communicate()
        LOGGER.info(jai)
        LOGGER.info(hind)
        if os.path.exists(uncompressed_file_name):
            try:
                os.remove(input_directory)
            except:
                pass
            return_name = uncompressed_file_name
            LOGGER.info(return_name)
    return return_name


async def progress_for_pyrogram_g(current, total, ud_type, message, start):
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion
        elapsed_time = time_formatter(milliseconds=elapsed_time)
        estimated_total_time = time_formatter(milliseconds=estimated_total_time)
        progress = "[{0}{1}] \nP: {2}%\n".format(
            ''.join([FINISHED_PROGRESS_STR for i in range(math.floor(percentage / 5))]),
            ''.join([UN_FINISHED_PROGRESS_STR for i in range(20 - math.floor(percentage / 5))]),
            round(percentage, 2))
        tmp = progress + "{0} of {1}\nSpeed: {2}/s\nETA: {3}\n".format(
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            estimated_total_time if estimated_total_time != '' else "0 s"
        )
        try:
            await message.edit("{}\n {}".format(ud_type, tmp))
        except:
            pass


def humanbytes(size):
    if not size:
        return ""
    power = 2 ** 10
    number = 0
    dict_power_n = {
        0: " ",
        1: "Ki",
        2: "Mi",
        3: "Gi",
        4: "Ti"
    }
    while size > power:
        size /= power
        number += 1
    return str(round(size, 2)) + " " + dict_power_n[number] + 'B'


def time_formatter(milliseconds):
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "") + \
        ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2]
