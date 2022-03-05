import os
import re
import time
import math
import json
import shutil
import aria2p
import asyncio
import logging
import aiohttp
import requests
import subprocess
from PIL import Image
from pyrogram import filters
from datetime import datetime
from hurry.filesize import size
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from pyrogram.errors import MessageNotModified
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaVideo, InputMediaAudio, InputMediaDocument
from tobrot import DEF_THUMB_NAIL_VID_S, INDEX_LINK, DESTINATION_FOLDER, RCLONE_CONFIG, TG_MAX_FILE_SIZE, MAX_TG_SPLIT_FILE_SIZE, REAL_DEBRID_KEY, TG_OFFENSIVE_API, DOWNLOAD_LOCATION, FINISHED_PROGRESS_STR, UN_FINISHED_PROGRESS_STR, ARIA_TWO_STARTED_PORT, MAX_TIME_TO_WAIT_FOR_TORRENTS_TO_START, CUSTOM_FILE_NAME, EDIT_SLEEP_TIME_OUT


MAGNETIC_LINK_REGEX = r"magnet\:\?xt\=urn\:btih\:([A-F\d]+)"
BASE_URL = "https://api.real-debrid.com/rest/1.0"


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
LOGGER = logging.getLogger(__name__)


async def is_admin(f, c, m):
    user = await c.get_chat_member(m.chat.id, m.from_user.id)
    return bool(user.status in ["creator", "administrator"])
admins = filters.create(is_admin)


async def AdminCheck(client, chat_id, user_id):
    SELF = await client.get_chat_member(
        chat_id=chat_id,
        user_id=user_id
    )
    admin_strings = [
        "creator",
        "administrator"
    ]
    if SELF.status not in admin_strings:
        return False
    else:
        return True


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


async def progress_for_pyrogram(current, total, ud_type, message, start):
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion
        elapsed_time = timeformatter(milliseconds=elapsed_time)
        estimated_total_time = timeformatter(milliseconds=estimated_total_time)
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
            if not message.photo:
                await message.edit_text(text="{}\n {}".format(ud_type, tmp))
            else:
                await message.edit_caption(caption="{}\n {}".format(ud_type, tmp))
        except:
            pass


def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'


def timeformatter(milliseconds):
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


async def aria_start():
    aria2_daemon_start_cmd = []
    aria2_daemon_start_cmd.append("aria2c")
    aria2_daemon_start_cmd.append("--daemon=true")
    aria2_daemon_start_cmd.append("--enable-rpc")
    aria2_daemon_start_cmd.append("--follow-torrent=mem")
    aria2_daemon_start_cmd.append("--max-connection-per-server=10")
    aria2_daemon_start_cmd.append("--min-split-size=10M")
    aria2_daemon_start_cmd.append("--rpc-listen-all=false")
    aria2_daemon_start_cmd.append(f"--rpc-listen-port={ARIA_TWO_STARTED_PORT}")
    aria2_daemon_start_cmd.append("--rpc-max-request-size=1024M")
    aria2_daemon_start_cmd.append("--seed-ratio=0.0")
    aria2_daemon_start_cmd.append("--seed-time=1")
    aria2_daemon_start_cmd.append("--split=10")
    aria2_daemon_start_cmd.append(f"--bt-stop-timeout={MAX_TIME_TO_WAIT_FOR_TORRENTS_TO_START}")
    LOGGER.info(aria2_daemon_start_cmd)
    process = await asyncio.create_subprocess_exec(
        *aria2_daemon_start_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    LOGGER.info(stdout)
    LOGGER.info(stderr)
    aria2 = aria2p.API(
        aria2p.Client(
            host="http://localhost",
            port=ARIA_TWO_STARTED_PORT,
            secret=""
        )
    )
    return aria2


def add_magnet(aria_instance, magnetic_link, c_file_name):
    options = None
    try:
        download = aria_instance.add_magnet(
            magnetic_link,
            options=options
        )
    except Exception as e:
        return False, "**#FAILED  #ERROR** \n" + f'(**Error** : "`{type(e).__name__ } : {e}`")' + " \n__Please Don't Send SLOW Links. Read **/help**__"
    else:
        return True, "" + download.gid + ""


def add_torrent(aria_instance, torrent_file_path):
    if torrent_file_path is None:
        return False, "**#FAILED  #ERROR** \n__Something Wrongings When Trying To Add **TORRENT** File__"
    if os.path.exists(torrent_file_path):
        try:
            download = aria_instance.add_torrent(
                torrent_file_path,
                uris=None,
                options=None,
                position=None
            )
        except Exception as e:
            return False, "**#FAILED  #ERROR** \n" + f'(**Error** : "`{type(e).__name__ } : {e}`")' + " \n__Please Don't Send SLOW Links. Read **/help**__"
        else:
            return True, "" + download.gid + ""
    else:
        return False, "**#FAILED  #ERROR** \n" + "Please try other sources to get workable link".title()


def add_url(aria_instance, text_url, c_file_name):
    options = None
    uris = [text_url]
    try:
        download = aria_instance.add_uris(
            uris,
            options=options
        )
    except Exception as e:
        return False, "**#FAILED  #ERROR** \n" + f'(**Error** : "`{type(e).__name__ } : {e}`")' + " \n__Please Don't Send SLOW Links. Read **/help**__"
    else:
        return True, "" + download.gid + ""


async def call_apropriate_function(aria_instance, incoming_link, c_file_name, sent_message_to_update_tg_p, is_zip, cstom_file_name, is_unzip, is_unrar, is_untar, user_message):
    if incoming_link.lower().startswith("magnet:"):
        sagtus, err_message = add_magnet(aria_instance, incoming_link, c_file_name)
    elif incoming_link.lower().endswith(".torrent"):
        sagtus, err_message = add_torrent(aria_instance, incoming_link)
    else:
        sagtus, err_message = add_url(aria_instance, incoming_link, c_file_name)
    if not sagtus:
        return sagtus, err_message
    LOGGER.info(err_message)
    await check_progress_for_dl(
        aria_instance,
        err_message,
        sent_message_to_update_tg_p,
        None
    )
    if incoming_link.startswith("magnet:"):
        err_message = await check_metadata(aria_instance, err_message)
        await asyncio.sleep(1)
        if err_message is not None:
            await check_progress_for_dl(
                aria_instance,
                err_message,
                sent_message_to_update_tg_p,
                None
            )
        else:
            return False, "can't get metadata \n\n#stopped"
    await asyncio.sleep(1)
    file = aria_instance.get_download(err_message)
    to_upload_file = file.name
    if is_zip:
        check_if_file = await create_archive(to_upload_file)
        if check_if_file is not None:
            to_upload_file = check_if_file
    if is_unzip:
        check_ifi_file = await unzip_me(to_upload_file)
        if check_ifi_file is not None:
            to_upload_file = check_ifi_file
    if is_unrar:
        check_ife_file = await unrar_me(to_upload_file)
        if check_ife_file is not None:
            to_upload_file = check_ife_file
    if is_untar:
        check_ify_file = await untar_me(to_upload_file)
        if check_ify_file is not None:
            to_upload_file = check_ify_file
    if to_upload_file:
        if CUSTOM_FILE_NAME:
            os.rename(to_upload_file, f"{CUSTOM_FILE_NAME}{to_upload_file}")
            to_upload_file = f"{CUSTOM_FILE_NAME}{to_upload_file}"
        else:
            to_upload_file = to_upload_file
    if cstom_file_name:
        os.rename(to_upload_file, cstom_file_name)
        to_upload_file = cstom_file_name
    else:
        to_upload_file = to_upload_file
    response = {}
    LOGGER.info(response)
    user_id = user_message.from_user.id
    print(user_id)
    final_response = await upload_to_tg(
        sent_message_to_update_tg_p,
        to_upload_file,
        user_id,
        response
    )
    LOGGER.info(final_response)
    try:
        message_to_send = ""
        for key_f_res_se in final_response:
            local_file_name = key_f_res_se
            message_id = final_response[key_f_res_se]
            channel_id = str(sent_message_to_update_tg_p.chat.id)[4:]
            private_link = f"https://t.me/c/{channel_id}/{message_id}"
            message_to_send += "👉 <a href='"
            message_to_send += private_link
            message_to_send += "'>"
            message_to_send += local_file_name
            message_to_send += "</a>"
            message_to_send += "\n"
        if message_to_send != "":
            mention_req_user = f"<a href='tg://user?id={user_id}'>Your Requested Files</a>\n\n"
            message_to_send = mention_req_user + message_to_send
            message_to_send = message_to_send + "\n\n" + "#uploads"
        else:
            message_to_send = "**#FAILED** : Faile To Upload Files. 😞😞"
        await user_message.reply_text(
            text=message_to_send,
            quote=True,
            disable_web_page_preview=True
        )
    except:
        pass
    return True, None


async def call_apropriate_function_g(aria_instance, incoming_link, c_file_name, sent_message_to_update_tg_p, is_zip, cstom_file_name, is_unzip, is_unrar, is_untar, user_message):
    if incoming_link.lower().startswith("magnet:"):
        sagtus, err_message = add_magnet(aria_instance, incoming_link, c_file_name)
    elif incoming_link.lower().endswith(".torrent"):
        sagtus, err_message = add_torrent(aria_instance, incoming_link)
    else:
        sagtus, err_message = add_url(aria_instance, incoming_link, c_file_name)
    if not sagtus:
        return sagtus, err_message
    LOGGER.info(err_message)
    await check_progress_for_dl(
        aria_instance,
        err_message,
        sent_message_to_update_tg_p,
        None
    )
    if incoming_link.startswith("magnet:"):
        err_message = await check_metadata(aria_instance, err_message)
        await asyncio.sleep(1)
        if err_message is not None:
            await check_progress_for_dl(
                aria_instance,
                err_message,
                sent_message_to_update_tg_p,
                None
            )
        else:
            return False, "can't get metadata \n\n#stopped"
    await asyncio.sleep(1)
    file = aria_instance.get_download(err_message)
    to_upload_file = file.name
    if is_zip:
        check_if_file = await create_archive(to_upload_file)
        if check_if_file is not None:
            to_upload_file = check_if_file
    if is_unzip:
        check_ifi_file = await unzip_me(to_upload_file)
        if check_ifi_file is not None:
            to_upload_file = check_ifi_file
    if is_unrar:
        check_ife_file = await unrar_me(to_upload_file)
        if check_ife_file is not None:
            to_upload_file = check_ife_file
    if is_untar:
        check_ify_file = await untar_me(to_upload_file)
        if check_ify_file is not None:
            to_upload_file = check_ify_file
    if to_upload_file:
        if CUSTOM_FILE_NAME:
            os.rename(to_upload_file, f"{CUSTOM_FILE_NAME}{to_upload_file}")
            to_upload_file = f"{CUSTOM_FILE_NAME}{to_upload_file}"
        else:
            to_upload_file = to_upload_file

    if cstom_file_name:
        os.rename(to_upload_file, cstom_file_name)
        to_upload_file = cstom_file_name
    else:
        to_upload_file = to_upload_file
    response = {}
    LOGGER.info(response)
    user_id = user_message.from_user.id
    print(user_id)
    final_response = await upload_to_gdrive(
        to_upload_file,
        sent_message_to_update_tg_p,
        user_message,
        user_id
    )


async def call_apropriate_function_t(to_upload_file_g, sent_message_to_update_tg_p, is_unzip, is_unrar, is_untar):
    to_upload_file = to_upload_file_g
    if is_unzip:
        check_ifi_file = await unzip_me(to_upload_file_g)
        if check_ifi_file is not None:
            to_upload_file = check_ifi_file
    if is_unrar:
        check_ife_file = await unrar_me(to_upload_file_g)
        if check_ife_file is not None:
            to_upload_file = check_ife_file
    if is_untar:
        check_ify_file = await untar_me(to_upload_file_g)
        if check_ify_file is not None:
            to_upload_file = check_ify_file
    response = {}
    LOGGER.info(response)
    user_id = sent_message_to_update_tg_p.reply_to_message.from_user.id
    final_response = await upload_to_gdrive(
        to_upload_file,
        sent_message_to_update_tg_p
    )
    LOGGER.info(final_response)


async def check_progress_for_dl(aria2, gid, event, previous_message):
    try:
        file = aria2.get_download(gid)
        complete = file.is_complete
        is_file = file.seeder
        if not complete:
            if not file.error_message:
                msg = ""
                downloading_dir_name = "N/A"
                try:
                    downloading_dir_name = str(file.name)
                except:
                    pass
                msg = f"\nDownloading File: `{downloading_dir_name}`"
                msg += f"\nSpeed: {file.download_speed_string()} 🔽 / {file.upload_speed_string()} 🔼"
                msg += f"\nProgress: {file.progress_string()}"
                msg += f"\nTotal Size: {file.total_length_string()}"
                if is_file is None :
                   msg += f"\n<b>Connections:</b> {file.connections}"
                else :
                   msg += f"\n<b>Info:</b>[ P : {file.connections} || S : {file.num_seeders} ]"
                msg += f"\nETA: {file.eta_string()}"
                msg += f"\nGID: <code>{gid}</code>"
                inline_keyboard = []
                ikeyboard = []
                ikeyboard.append(InlineKeyboardButton("❌ Cancel ❌", callback_data=(f"cancel {gid}").encode("UTF-8")))
                inline_keyboard.append(ikeyboard)
                reply_markup = InlineKeyboardMarkup(inline_keyboard)
                LOGGER.info(msg)
                if msg != previous_message:
                    await event.edit(msg, reply_markup=reply_markup)
                    previous_message = msg
            else:
                msg = file.error_message
                await asyncio.sleep(EDIT_SLEEP_TIME_OUT)
                await event.edit(f"`{msg}`")
                return False
            await asyncio.sleep(EDIT_SLEEP_TIME_OUT)
            await check_progress_for_dl(aria2, gid, event, previous_message)
        else:
            await asyncio.sleep(EDIT_SLEEP_TIME_OUT)
            await event.edit(f"File Downloaded Successfully : `{file.name}`")
            return True
    except aria2p.client.ClientException:
        pass
    except MessageNotModified:
        pass
    except RecursionError:
        file.remove(force=True)
        await event.edit(
            "Download Auto Cancelled :\n\n"
            "Your Torrent / Link Is Dead.".format(file.name)
        )
        return False
    except Exception as e:
        LOGGER.info(str(e))
        if " not found" in str(e) or "'file'" in str(e):
            await event.edit("Download Cancelled :\n<code>{}</code>".format(file.name))
            return False
        else:
            LOGGER.info(str(e))
            await event.edit(f'**#ERROR** : (**Error** : "`{type(e).__name__ } : {str(e)}`")')
            return False


async def check_metadata(aria2, gid):
    file = aria2.get_download(gid)
    LOGGER.info(file)
    if not file.followed_by_ids:
        return None
    new_gid = file.followed_by_ids[0]
    LOGGER.info("Changing GID " + gid + " To " + new_gid)
    return new_gid


async def request_download(url, file_name, r_user_id):
    directory_path = os.path.join(DOWNLOAD_LOCATION, str(r_user_id), str(time.time()))
    if not os.path.isdir(directory_path):
        os.makedirs(directory_path)
    local_file_path = os.path.join(directory_path, file_name)
    command_to_exec = [
        "wget",
        "-O",
        local_file_path,
        url
    ]
    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    final_m_r = e_response + "\n\n\n" + t_response
    if os.path.exists(local_file_path):
        return True, local_file_path
    else:
        return False, final_m_r


async def down_load_media_f(client, message):
    user_id = message.from_user.id
    print(user_id)
    mess_age = await message.reply_text("...", quote=True)
    if not os.path.isdir(DOWNLOAD_LOCATION):
        os.makedirs(DOWNLOAD_LOCATION)
    if message.reply_to_message is not None:
        start_t = datetime.now()
        download_location = DOWNLOAD_LOCATION + "/"
        c_time = time.time()
        the_real_download_location = await client.download_media(
            message=message.reply_to_message,
            file_name=download_location,
            progress=progress_for_pyrogram,
            progress_args=(
                "Trying To Download...", mess_age, c_time
            )
        )
        end_t = datetime.now()
        ms = (end_t - start_t).seconds
        print(the_real_download_location)
        await asyncio.sleep(10)
        await mess_age.edit_text(f"Downloaded To <code>{the_real_download_location}</code> In <u>{ms}</u> Seconds")
        gk = subprocess.Popen(['mv', f'{the_real_download_location}', '/app/'], stdout = subprocess.PIPE)
        out = gk.communicate()
        the_real_download_location_g = os.path.basename(the_real_download_location)
        if len(message.command) > 1:
            if message.command[1] == "unzip":
                file_upload = await unzip_me(the_real_download_location_g)
                if file_upload is not None:
                    g_response = await upload_to_gdrive(file_upload, mess_age, message, user_id)
                    LOGGER.info(g_response)
            elif message.command[1] == "unrar":
                file_uploade = await unrar_me(the_real_download_location_g)
                if file_uploade is not None:
                    gk_response = await upload_to_gdrive(file_uploade, mess_age, message, user_id)
                    LOGGER.info(gk_response)
            elif message.command[1] == "untar":
                 file_uploadg = await untar_me(the_real_download_location_g)
                 if file_uploadg is not None:
                     gau_response = await upload_to_gdrive(file_uploadg, mess_age, message, user_id)
                     LOGGER.info(gau_response)
        else:
            gaut_response = await upload_to_gdrive(the_real_download_location_g, mess_age, message, user_id)
            LOGGER.info(gaut_response)
    else:
        await mess_age.edit_text("Reply To A Telegram Media, To Upload To The Cloud Drive.")


def extract_url_from_entity(entities, text):
    url = None
    for entity in entities:
        if entity.type == "text_link":
            url = entity.url
        elif entity.type == "url":
            o = entity.offset
            l = entity.length
            url = text[o:o + l]
    return url


async def extract_link(message, type_o_request):
    custom_file_name = None
    url = None
    youtube_dl_username = None
    youtube_dl_password = None
    if message is None:
        url = None
        custom_file_name = None
    elif message.text is not None:
        if message.text.lower().startswith("magnet:"):
            url = message.text.strip()
        elif "|" in message.text:
            url_parts = message.text.split("|")
            if len(url_parts) == 2:
                url = url_parts[0]
                custom_file_name = url_parts[1]
            elif len(url_parts) == 4:
                url = url_parts[0]
                custom_file_name = url_parts[1]
                youtube_dl_username = url_parts[2]
                youtube_dl_password = url_parts[3]
        elif message.entities is not None:
            url = extract_url_from_entity(message.entities, message.text)
        else:
            url = message.text.strip()
    elif message.document is not None:
        if message.document.file_name.lower().endswith(".torrent"):
            url = await message.download()
            custom_file_name = message.caption
    elif message.caption is not None:
        if "|" in message.caption:
            url_parts = message.caption.split("|")
            if len(url_parts) == 2:
                url = url_parts[0]
                custom_file_name = url_parts[1]
            elif len(url_parts) == 4:
                url = url_parts[0]
                custom_file_name = url_parts[1]
                youtube_dl_username = url_parts[2]
                youtube_dl_password = url_parts[3]
        elif message.caption_entities is not None:
            url = extract_url_from_entity(message.caption_entities, message.caption)
        else:
            url = message.caption.strip()
    elif message.entities is not None:
        url = message.text
    if url is not None:
        url = url.strip()
    if custom_file_name is not None:
        custom_file_name = custom_file_name.strip()
    if youtube_dl_username is not None:
        youtube_dl_username = youtube_dl_username.strip()
    if youtube_dl_password is not None:
        youtube_dl_password = youtube_dl_password.strip()
    LOGGER.info(TG_OFFENSIVE_API)
    if TG_OFFENSIVE_API is not None:
        try:
            async with aiohttp.ClientSession() as session:
                api_url = TG_OFFENSIVE_API.format(
                    i=url,
                    m=custom_file_name,
                    t=type_o_request
                )
                LOGGER.info(api_url)
                async with session.get(api_url) as resp:
                    suats = int(resp.status)
                    err = await resp.text()
                    if suats != 200:
                        url = None
                        custom_file_name = err
        except:
            pass
    return url, custom_file_name, youtube_dl_username, youtube_dl_password


async def take_screen_shot(video_file, output_directory, ttl):
    out_put_file_name = os.path.join(
        output_directory,
        str(time.time()) + ".jpg"
    )
    if video_file.upper().endswith(("MKV", "MP4", "WEBM")):
        file_genertor_command = [
            "ffmpeg",
            "-ss",
            str(ttl),
            "-i",
            video_file,
            "-vframes",
            "1",
            out_put_file_name
        ]
        process = await asyncio.create_subprocess_exec(
            *file_genertor_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        e_response = stderr.decode().strip()
        t_response = stdout.decode().strip()
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    else:
        return None


def extract_info_hash_from_ml(magnetic_link):
    ml_re_match = re.search(MAGNETIC_LINK_REGEX, magnetic_link)
    if ml_re_match is not None:
        return ml_re_match.group(1)


async def fetch(session, url, data):
    async with session.post(url, data=data) as response:
        return await response.json()


async def extract_it(restricted_link, custom_file_name):
    async with aiohttp.ClientSession() as session:
        url_to_send = BASE_URL + "/unrestrict/link?auth_token=" + REAL_DEBRID_KEY
        to_send_data = {
            "link": restricted_link
        }
        html = await fetch(session, url_to_send, to_send_data)
        LOGGER.info(html)
        downloadable_url = html.get("download")
        original_file_name = custom_file_name
        if original_file_name is None:
            original_file_name = html.get("filename")
        return downloadable_url, original_file_name


async def split_large_files(input_file):
    working_directory = os.path.dirname(os.path.abspath(input_file))
    new_working_directory = os.path.join(
        working_directory,
        str(time.time())
    )
    if not os.path.isdir(new_working_directory):
        os.makedirs(new_working_directory)
    if False:
        # handle video / audio files here
        metadata = extractMetadata(createParser(input_file))
        total_duration = 0
        if metadata.has("duration"):
            total_duration = metadata.get('duration').seconds
        # proprietary logic to get the seconds to trim (at)
        LOGGER.info(total_duration)
        total_file_size = os.path.getsize(input_file)
        LOGGER.info(total_file_size)
        minimum_duration = (total_duration / total_file_size) * (MAX_TG_SPLIT_FILE_SIZE)
        LOGGER.info(minimum_duration)
        # END: proprietary
        start_time = 0
        end_time = minimum_duration
        base_name = os.path.basename(input_file)
        input_extension = base_name.split(".")[-1]
        LOGGER.info(input_extension)
        i = 0
        while end_time < total_duration:
            LOGGER.info(i)
            parted_file_name = ""
            parted_file_name += str(i).zfill(5)
            parted_file_name += str(base_name)
            parted_file_name += "_PART_"
            parted_file_name += str(start_time)
            parted_file_name += "."
            parted_file_name += str(input_extension)
            output_file = os.path.join(new_working_directory, parted_file_name)
            LOGGER.info(output_file)
            LOGGER.info(await cult_small_video(
                input_file,
                output_file,
                str(start_time),
                str(end_time)
            ))
            start_time = end_time
            end_time = end_time + minimum_duration
            i = i + 1
    else:
        o_d_t = os.path.join(
            new_working_directory,
            os.path.basename(input_file)
        )
        o_d_t = o_d_t + "."
        file_genertor_command = [
            "split",
            "--numeric-suffixes=1",
            "--suffix-length=5",
            f"--bytes={MAX_TG_SPLIT_FILE_SIZE}",
            input_file,
            o_d_t
        ]
        process = await asyncio.create_subprocess_exec(
            *file_genertor_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        e_response = stderr.decode().strip()
        t_response = stdout.decode().strip()
    return new_working_directory


async def cult_small_video(video_file, out_put_file_name, start_time, end_time):
    file_genertor_command = [
        "ffmpeg",
        "-hide_banner",
        "-i",
        video_file,
        "-ss",
        start_time,
        "-to",
        end_time,
        "-async",
        "1",
        "-strict",
        "-2",
        "-c",
        "copy",
        out_put_file_name
    ]
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    LOGGER.info(t_response)
    return out_put_file_name


def getFolderSize(p):
    from functools import partial
    prepend = partial(os.path.join, p)
    return sum([(os.path.getsize(f) if os.path.isfile(f) else getFolderSize(f)) for f in map(prepend, os.listdir(p))])


async def upload_to_tg(  message, local_file_name, from_user, dict_contatining_uploaded_files, edit_media=False):
    LOGGER.info(local_file_name)
    base_file_name = os.path.basename(local_file_name)
    caption_str = ""
    caption_str += "<code>"
    caption_str += base_file_name
    caption_str += "</code>"
    if os.path.isdir(local_file_name):
        directory_contents = os.listdir(local_file_name)
        directory_contents.sort()
        LOGGER.info(directory_contents)
        new_m_esg = message
        if not message.photo:
            new_m_esg = await message.reply_text(
                "Found {} Files".format(len(directory_contents)),
                quote=True
            )
        for single_file in directory_contents:
            await upload_to_tg(
                new_m_esg,
                os.path.join(local_file_name, single_file),
                from_user,
                dict_contatining_uploaded_files,
                edit_media
            )
    else:
        if os.path.getsize(local_file_name) > TG_MAX_FILE_SIZE:
            LOGGER.info("TODO")
            d_f_s = humanbytes(os.path.getsize(local_file_name))
            i_m_s_g = await message.reply_text(
                "Telegram Doesn't Support Uploading This File.\n"
                f"Detected File Size : {d_f_s} 😡\n"
                "\n🤖 Trying To Split The Files 🌝🌝🌚"
            )
            splitted_dir = await split_large_files(local_file_name)
            totlaa_sleif = os.listdir(splitted_dir)
            totlaa_sleif.sort()
            number_of_files = len(totlaa_sleif)
            LOGGER.info(totlaa_sleif)
            ba_se_file_name = os.path.basename(local_file_name)
            await i_m_s_g.edit_text(
                f"Detected File Size: {d_f_s} 😡\n"
                f"<code>{ba_se_file_name}</code> Splitted Into {number_of_files} Files.\n"
                "Trying To Upload To Telegram, Now..."
            )
            for le_file in totlaa_sleif:
                await upload_to_tg(
                    message,
                    os.path.join(splitted_dir, le_file),
                    from_user,
                    dict_contatining_uploaded_files
                )
        else:
            sent_message = await upload_single_file(
                message,
                local_file_name,
                caption_str,
                from_user,
                edit_media
            )
            if sent_message is not None:
                dict_contatining_uploaded_files[os.path.basename(local_file_name)] = sent_message.message_id
    return dict_contatining_uploaded_files


async def upload_to_gdrive(file_upload, message, messa_ge, g_id):
    await asyncio.sleep(EDIT_SLEEP_TIME_OUT)
    del_it = await message.edit_text("Uploading To ☁️ CLOUD ☁️")
    with open('rclone.conf', 'a', newline="\n", encoding = 'utf-8') as fole:
        fole.write("[DRIVE]\n")
        fole.write(f"{RCLONE_CONFIG}")
    destination = f'{DESTINATION_FOLDER}'
    if os.path.isfile(file_upload):
        g_au = ['rclone', 'copy', '--config=/app/rclone.conf', f'/app/{file_upload}', 'DRIVE:'f'{destination}', '-vvv']
        tmp = await asyncio.create_subprocess_exec(*g_au, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        pro, cess = await tmp.communicate()
        LOGGER.info(pro.decode('utf-8'))
        LOGGER.info(cess.decode('utf-8'))
        gk_file = re.escape(file_upload)
        LOGGER.info(gk_file)
        with open('filter.txt', 'w+', encoding = 'utf-8') as filter:
            print(f"+ {gk_file}\n- *", file=filter)
            
        t_a_m = ['rclone', 'lsf', '--config=/app/rclone.conf', '-F', 'i', "--filter-from=/app/filter.txt", "--files-only", 'DRIVE:'f'{destination}']
        gau_tam = await asyncio.create_subprocess_exec(*t_a_m, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        gau, tam = await gau_tam.communicate()
        LOGGER.info(gau)
        gautam = gau.decode("utf-8")
        LOGGER.info(gautam)
        LOGGER.info(tam.decode('utf-8'))
        gauti = f"https://drive.google.com/file/d/{gautam}/view?usp=drivesdk"
        gau_link = re.search("(?P<url>https?://[^\s]+)", gauti).group("url")
        LOGGER.info(gau_link)
        prgs = size(os.path.getsize(file_upload))
        LOGGER.info(prgs)
        button = []
        button.append([InlineKeyboardButton(text="☁️ G-Drive Link ☁️", url=f"{gau_link}")])
        if INDEX_LINK:
            indexurl = f"{INDEX_LINK}/{file_upload}"
            tam_link = requests.utils.requote_uri(indexurl)
            LOGGER.info(tam_link)
            button.append([InlineKeyboardButton(text="ℹ️ Index Link ℹ️", url=f"{tam_link}")])
        button_markup = InlineKeyboardMarkup(button)
        await asyncio.sleep(EDIT_SLEEP_TIME_OUT)
        await messa_ge.reply_text(f"⭕️ **FILE NAME** : {file_upload}\n\n⭕️ **FILE SIZE** : {prgs}\n\n⭕️ **Your File Has Been Uploaded** 🥳\n\n⭕️ **©️ @KL35Ronaldo .**", reply_markup=button_markup)
        os.remove(file_upload)
        await del_it.delete()
    else:
        tt= os.path.join(destination, file_upload)
        LOGGER.info(tt)
        t_am = ['rclone', 'copy', '--config=/app/rclone.conf', f'/app/{file_upload}', 'DRIVE:'f'{tt}', '-vvv']
        tmp = await asyncio.create_subprocess_exec(*t_am, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        pro, cess = await tmp.communicate()
        LOGGER.info(pro.decode('utf-8'))
        LOGGER.info(cess.decode('utf-8'))
        g_file = re.escape(file_upload)
        LOGGER.info(g_file)
        with open('filter1.txt', 'w+', encoding = 'utf-8') as filter1:
            print(f"+ {g_file}/\n- *", file=filter1)
        g_a_u = ['rclone', 'lsf', '--config=/app/rclone.conf', '-F', 'i', "--filter-from=/app/filter1.txt", "--dirs-only", 'DRIVE:'f'{destination}']
        gau_tam = await asyncio.create_subprocess_exec(*g_a_u, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        gau, tam = await gau_tam.communicate()
        LOGGER.info(gau)
        gautam = gau.decode("utf-8")
        LOGGER.info(gautam)
        LOGGER.info(tam.decode('utf-8'))
        gautii = f"https://drive.google.com/folderview?id={gautam}"
        gau_link = re.search("(?P<url>https?://[^\s]+)", gautii).group("url")
        LOGGER.info(gau_link)
        prgs = size(getFolderSize(file_upload))
        LOGGER.info(prgs)
        button = []
        button.append([InlineKeyboardButton(text="☁️ G-Drive Link ☁️", url=f"{gau_link}")])
        if INDEX_LINK:
            indexurl = f"{INDEX_LINK}/{file_upload}/"
            tam_link = requests.utils.requote_uri(indexurl)
            LOGGER.info(tam_link)
            button.append([InlineKeyboardButton(text="ℹ️ Index Link ℹ️", url=f"{tam_link}")])
        button_markup = InlineKeyboardMarkup(button)
        await asyncio.sleep(EDIT_SLEEP_TIME_OUT)
        await messa_ge.reply_text(f"🤖 : Folder Has Been Uploaded Successfully To {tt} in your Cloud <a href='tg://user?id={g_id}'>🤒</a>\n📀 Size: {prgs}", reply_markup=button_markup)
        shutil.rmtree(file_upload)
        await del_it.delete()


async def upload_single_file(message, local_file_name, caption_str, from_user, edit_media):
    await asyncio.sleep(EDIT_SLEEP_TIME_OUT)
    sent_message = None
    start_time = time.time()
    thumbnail_location = os.path.join(
        DOWNLOAD_LOCATION,
        "thumbnails",
        str(from_user) + ".jpg"
    )
    LOGGER.info(thumbnail_location)
    try:
        message_for_progress_display = message
        if not edit_media:
            message_for_progress_display = await message.reply_text(
                "Starting Upload Of {}".format(os.path.basename(local_file_name))
            )
        if local_file_name.upper().endswith(("WEBM")):
            metadata = extractMetadata(createParser(local_file_name))
            duration = 0
            if metadata.has("duration"):
                duration = metadata.get('duration').seconds
            width = 0
            height = 0
            thumb_image_path = None
            if os.path.exists(thumbnail_location):
                thumb_image_path = await copy_file(
                    thumbnail_location,
                    os.path.dirname(os.path.abspath(local_file_name))
                )
            else:
                thumb_image_path = await take_screen_shot(
                    local_file_name,
                    os.path.dirname(os.path.abspath(local_file_name)),
                    (duration / 2)
                )
                if os.path.exists(thumb_image_path):
                    metadata = extractMetadata(createParser(thumb_image_path))
                    if metadata.has("width"):
                        width = metadata.get("width")
                    if metadata.has("height"):
                        height = metadata.get("height")
                    Image.open(thumb_image_path).convert(
                        "RGB"
                    ).save(thumb_image_path)
                    img = Image.open(thumb_image_path)
                    img.resize((320, height))
                    img.save(thumb_image_path, "JPEG")
            thumb = None
            if thumb_image_path is not None and os.path.isfile(thumb_image_path):
                thumb = thumb_image_path
            if edit_media and message.photo:
                await asyncio.sleep(EDIT_SLEEP_TIME_OUT)
                sent_message = await message.edit_media(
                    media=InputMediaVideo(
                        media=local_file_name,
                        thumb=thumb,
                        caption=caption_str,
                        parse_mode="html",
                        width=width,
                        height=height,
                        duration=duration,
                        supports_streaming=True
                    )
                )
            else:
                sent_message = await message.reply_video(
                    video=local_file_name,
                    caption=caption_str,
                    parse_mode="html",
                    duration=duration,
                    width=width,
                    height=height,
                    thumb=thumb,
                    supports_streaming=True,
                    disable_notification=True,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        "Trying To Upload",
                        message_for_progress_display,
                        start_time
                    )
                )
            if thumb is not None:
                os.remove(thumb)
        elif local_file_name.upper().endswith(("MP3", "M4A", "M4B", "FLAC", "WAV")):
            metadata = extractMetadata(createParser(local_file_name))
            duration = 0
            title = ""
            artist = ""
            if metadata.has("duration"):
                duration = metadata.get('duration').seconds
            if metadata.has("title"):
                title = metadata.get("title")
            if metadata.has("artist"):
                artist = metadata.get("artist")
            thumb_image_path = None
            if os.path.isfile(thumbnail_location):
                thumb_image_path = await copy_file(
                    thumbnail_location,
                    os.path.dirname(os.path.abspath(local_file_name))
                )
            thumb = None
            if thumb_image_path is not None and os.path.isfile(thumb_image_path):
                thumb = thumb_image_path
            if edit_media and message.photo:
                await asyncio.sleep(EDIT_SLEEP_TIME_OUT)
                sent_message = await message.edit_media(
                    media=InputMediaAudio(
                        media=local_file_name,
                        thumb=thumb,
                        caption=caption_str,
                        parse_mode="html",
                        duration=duration,
                        performer=artist,
                        title=title
                    )
                )
            else:
                sent_message = await message.reply_audio(
                    audio=local_file_name,
                    caption=caption_str,
                    parse_mode="html",
                    duration=duration,
                    performer=artist,
                    title=title,
                    thumb=thumb,
                    disable_notification=True,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        "Trying To Upload",
                        message_for_progress_display,
                        start_time
                    )
                )
            if thumb is not None:
                os.remove(thumb)
        else:
            thumb_image_path = None
            if os.path.isfile(thumbnail_location):
                thumb_image_path = await copy_file(
                    thumbnail_location,
                    os.path.dirname(os.path.abspath(local_file_name))
                )
            thumb = None
            if thumb_image_path is not None and os.path.isfile(thumb_image_path):
                thumb = thumb_image_path
            if edit_media and message.photo:
                sent_message = await message.edit_media(
                    media=InputMediaDocument(
                        media=local_file_name,
                        thumb=thumb,
                        caption=caption_str,
                        parse_mode="html"
                    )
                )
            else:
                sent_message = await message.reply_document(
                    document=local_file_name,
                    thumb=thumb,
                    caption=caption_str,
                    parse_mode="html",
                    disable_notification=True,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        "Trying To Upload",
                        message_for_progress_display,
                        start_time
                    )
                )
            if thumb is not None:
                os.remove(thumb)
    except Exception as e:
        await message_for_progress_display.edit_text("**#FAILED  #ERROR** \n" + f'(**Error** : "`{type(e).__name__ } : {e}`")')
    else:
        if message.message_id != message_for_progress_display.message_id:
            await message_for_progress_display.delete()
    os.remove(local_file_name)
    return sent_message


async def youtube_dl_call_back(bot, update):
    LOGGER.info(update)
    cb_data = update.data
    tg_send_type, youtube_dl_format, youtube_dl_ext = cb_data.split("|")
    current_user_id = update.message.reply_to_message.from_user.id
    current_touched_user_id = update.from_user.id
    if current_user_id != current_touched_user_id:
        await bot.answer_callback_query(
            callback_query_id=update.id,
            text="Who Are You? 🤪🤔🤔🤔",
            show_alert=True,
            cache_time=0
        )
        return False, None

    user_working_dir = os.path.join(DOWNLOAD_LOCATION, str(current_user_id))
    if not os.path.isdir(user_working_dir):
        await bot.delete_messages(
            chat_id=update.message.chat.id,
            message_ids=[
                update.message.message_id,
                update.message.reply_to_message.message_id,
            ],
            revoke=True
        )
        return
    save_ytdl_json_path = user_working_dir + \
        "/" + str("ytdleech") + ".json"
    try:
        with open(save_ytdl_json_path, "r", encoding="utf8") as f:
            response_json = json.load(f)
        os.remove(save_ytdl_json_path)
    except (FileNotFoundError) as e:
        await bot.delete_messages(
            chat_id=update.message.chat.id,
            message_ids=[
                update.message.message_id,
                update.message.reply_to_message.message_id,
            ],
            revoke=True
        )
        return False
    response_json = response_json[0]
    youtube_dl_url = response_json.get("webpage_url")
    LOGGER.info(youtube_dl_url)
    custom_file_name = "%(title)s.%(ext)s"
    LOGGER.info(custom_file_name)
    await update.message.edit_caption(
        caption="Trying to Download"
    )
    description = "@PublicLeech"
    if "fulltitle" in response_json:
        description = response_json["fulltitle"][0:1021]
    tmp_directory_for_each_user = os.path.join(
        DOWNLOAD_LOCATION,
        str(update.message.message_id)
    )
    if not os.path.isdir(tmp_directory_for_each_user):
        os.makedirs(tmp_directory_for_each_user)
    download_directory = tmp_directory_for_each_user
    download_directory = os.path.join(tmp_directory_for_each_user, custom_file_name)
    command_to_exec = []
    if tg_send_type == "audio":
        command_to_exec = [
            "youtube-dl",
            "-c",
            "--prefer-ffmpeg",
            "--extract-audio",
            "--audio-format", youtube_dl_ext,
            "--audio-quality", youtube_dl_format,
            youtube_dl_url,
            "-o", download_directory,
        ]
    else:
        minus_f_format = youtube_dl_format
        if "youtu" in youtube_dl_url:
            for for_mat in response_json["formats"]:
                format_id = for_mat.get("format_id")
                if format_id == youtube_dl_format:
                    acodec = for_mat.get("acodec")
                    vcodec = for_mat.get("vcodec")
                    if acodec == "none" or vcodec == "none":
                        minus_f_format = youtube_dl_format + "+bestaudio"
                    break
        command_to_exec = [
            "youtube-dl",
            "-c",
            "--embed-subs",
            "-f", minus_f_format,
            "--hls-prefer-ffmpeg", youtube_dl_url,
            "-o", download_directory,
        ]
    command_to_exec.append("--no-warnings")
    command_to_exec.append("--restrict-filenames")
    if "hotstar" in youtube_dl_url:
        command_to_exec.append("--geo-bypass-country")
        command_to_exec.append("IN")
    LOGGER.info(command_to_exec)
    start = datetime.now()
    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    ad_string_to_replace = "Please Report This Issue On https://yt-dl.org/bug . Make Sure You Are Using The Latest Version, See https://yt-dl.org/update On How To Update. Be Sure To Call youtube-dl With The --verbose Flag And Include Its Complete Output."
    if e_response and ad_string_to_replace in e_response:
        error_message = e_response.replace(ad_string_to_replace, "")
        await update.message.edit_caption(
            caption=error_message
        )
        return False, None
    if t_response:
        end_one = datetime.now()
        time_taken_for_download = (end_one -start).seconds
        dir_contents = len(os.listdir(tmp_directory_for_each_user))
        await update.message.edit_caption(
            caption=f"Found {dir_contents} Files"
        )
        user_id = update.from_user.id
        print(tmp_directory_for_each_user)
        if os.path.exists('blame_my_knowledge.txt'):
            for a, b, c in os.walk(tmp_directory_for_each_user):
                print(a)
                for d in c:
                    e = os.path.join(a, d)
                    print(e)
                    gaut_am = os.path.basename(e)
                    print(gaut_am)
                    liop = subprocess.Popen(["mv", f'{e}', "/app/"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    o, e = liop.communicate()
                    print(o)
                    print(e)
            final_response = await upload_to_gdrive(
                gaut_am,
                update.message,
                update.message.reply_to_message,
                user_id
            )
        else:
            final_response = await upload_to_tg(
                update.message,
                tmp_directory_for_each_user,
                user_id,
                {},
                True
            )
        LOGGER.info(final_response)
        try:
            shutil.rmtree(tmp_directory_for_each_user)
            os.remove('blame_my_knowledge.txt')
        except:
            pass


async def extract_youtube_dl_formats(url, yt_dl_user_name, yt_dl_pass_word, user_working_dir):
    command_to_exec = [
        "youtube-dl",
        "--no-warnings",
        "--youtube-skip-dash-manifest",
        "-j",
        url
    ]
    if "hotstar" in url:
        command_to_exec.append("--geo-bypass-country")
        command_to_exec.append("IN")
    if yt_dl_user_name is not None:
        command_to_exec.append("--username")
        command_to_exec.append(yt_dl_user_name)
    if yt_dl_pass_word is not None:
        command_to_exec.append("--password")
        command_to_exec.append(yt_dl_pass_word)
    LOGGER.info(command_to_exec)
    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    LOGGER.info(e_response)
    t_response = stdout.decode().strip()
    LOGGER.info(t_response)
    if e_response:
        error_message = e_response.replace(
            "Please Report This Issue On https://yt-dl.org/bug . Make Sure You Are Using The Latest Version, See https://yt-dl.org/update On How To Update. Be Sure To Call youtube-dl With The --verbose Flag And Include Its Complete Output.", ""
        )
        return None, error_message, None
    if t_response:
        x_reponse = t_response
        response_json = []
        if "\n" in x_reponse:
            for yu_r in x_reponse.split("\n"):
                response_json.append(json.loads(yu_r))
        else:
            response_json.append(json.loads(x_reponse))
        save_ytdl_json_path = user_working_dir + \
            "/" + str("ytdleech") + ".json"
        with open(save_ytdl_json_path, "w", encoding="utf8") as outfile:
            json.dump(response_json, outfile, ensure_ascii=False)
        inline_keyboard = []
        thumb_image = DEF_THUMB_NAIL_VID_S
        for current_r_json in response_json:
            thumb_image = current_r_json.get("thumbnail", thumb_image)
            duration = None
            if "duration" in current_r_json:
                duration = current_r_json["duration"]
            if "formats" in current_r_json:
                for formats in current_r_json["formats"]:
                    format_id = formats.get("format_id")
                    format_string = formats.get("format_note")
                    if format_string is None:
                        format_string = formats.get("format")
                    format_ext = formats.get("ext")
                    approx_file_size = ""
                    if "filesize" in formats:
                        approx_file_size = humanbytes(formats["filesize"])
                    dipslay_str_uon = " " + format_string + " (" + format_ext.upper() + ") " + approx_file_size + " "
                    cb_string_video = "{}|{}|{}".format(
                        "video", format_id, format_ext)
                    ikeyboard = []
                    if "drive.google.com" in url:
                        if format_id == "source":
                            ikeyboard = [
                                InlineKeyboardButton(
                                    dipslay_str_uon,
                                    callback_data=(cb_string_video).encode("UTF-8")
                                )
                            ]
                    else:
                        if format_string is not None and not "audio only" in format_string:
                            ikeyboard = [
                                InlineKeyboardButton(
                                    dipslay_str_uon,
                                    callback_data=(cb_string_video).encode("UTF-8")
                                )
                            ]
                        else:
                            ikeyboard = [
                                InlineKeyboardButton(
                                    "SVideo [" +
                                    "] ( " +
                                    approx_file_size + " )",
                                    callback_data=(cb_string_video).encode("UTF-8")
                                )
                            ]
                    inline_keyboard.append(ikeyboard)
                if duration is not None:
                    cb_string_64 = "{}|{}|{}".format("audio", "64k", "mp3")
                    cb_string_128 = "{}|{}|{}".format("audio", "128k", "mp3")
                    cb_string = "{}|{}|{}".format("audio", "320k", "mp3")
                    inline_keyboard.append([
                        InlineKeyboardButton(
                            "MP3 " + "(" + "64 kbps" + ")", callback_data=cb_string_64.encode("UTF-8")),
                        InlineKeyboardButton(
                            "MP3 " + "(" + "128 kbps" + ")", callback_data=cb_string_128.encode("UTF-8"))
                    ])
                    inline_keyboard.append([
                        InlineKeyboardButton(
                            "MP3 " + "(" + "320 kbps" + ")", callback_data=cb_string.encode("UTF-8"))
                    ])
            else:
                format_id = current_r_json["format_id"]
                format_ext = current_r_json["ext"]
                cb_string_video = "{}|{}|{}".format(
                    "video", format_id, format_ext)
                inline_keyboard.append([
                    InlineKeyboardButton(
                        "SVideo",
                        callback_data=(cb_string_video).encode("UTF-8")
                    )
                ])
            break
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        succss_mesg = "**__Select The Desired Format __**: 👇 \n**#Note** : __Mentioned File Size Might Be Approximate__"
        return thumb_image, succss_mesg, reply_markup


async def yt_playlist_downg(message, i_m_sefg, G_DRIVE):
    url = message.text
    usr = message.message_id
    messa_ge = i_m_sefg.reply_to_message
    fol_der = f"{usr}youtube"
    print(url)
    print(usr)
    print(messa_ge)
    print(fol_der)
    try:
        os.mkdir(fol_der)
    except:
        pass
    cmd = ["youtube-dl", "-i", "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4", "-o", f"{fol_der}/%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s", f"{url}"]
    gau_tam = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    gau, tam = await gau_tam.communicate()
    LOGGER.info(gau.decode('utf-8'))
    LOGGER.info(tam.decode('utf-8'))
    e_response = tam.decode().strip()
    ad_string_to_replace = "Please Report This Issue On https://yt-dl.org/bug . Make Sure You Are Using The Latest Version, See https://yt-dl.org/update On How To Update. Be Sure To Call youtube-dl With The --verbose Flag And Include Its Complete Output."
    if e_response and ad_string_to_replace in e_response:
        error_message = e_response.replace(ad_string_to_replace, "")
        await i_m_sefg.edit_text(
            error_message
        )
        return False, None
    if G_DRIVE:
        get_g = os.listdir(fol_der)
        print(get_g)
        for ga_u in get_g:
            print(ga_u)
            ta_m = os.path.join(fol_der, ga_u)
            print(ta_m)
            shutil.move(ta_m, './')
            await upload_to_gdrive(ga_u, i_m_sefg, message, usr)
    else:
        final_response = await upload_to_tg(i_m_sefg, fol_der, usr, {})
        print(final_response)
    try:
        shutil.rmtree(fol_der)
    except:
        pass
