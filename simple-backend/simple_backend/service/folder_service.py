"""
 Copyright (C) 2023 Università degli Studi di Camerino.
 Authors: Alessandro Antinori, Rosario Capparuccia, Riccardo Coltrinari, Flavio Corradini, Marco Piangerelli, Barbara Re, Marco Scarpetta, Luca Mozzoni, Vincenzo Nucci

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as
 published by the Free Software Foundation, either version 3 of the
 License, or (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <https://www.gnu.org/licenses/>.
 """

import os
import stat
import shutil
import time
from typing import List
from schemas.file_schemas import FileConfigSchema

BASE_FOLDER = '/tmp/data/'

def __get_user_folders_path(user_name):
    return BASE_FOLDER + user_name + '/folders'

def __get_folder_path(user_name, folder_name):
    return os.path.join(__get_user_folders_path(user_name), folder_name)

def __get_file_path(user_name, folder_name, file_name):
    return os.path.join(__get_folder_path(user_name, folder_name), file_name)


def get_folder_names(user: str) -> List[str]:
    """ Returns info about the folders. """
    base_folder = __get_user_folders_path(user)
    os.makedirs(base_folder, exist_ok=True)
    folders = []

    for folder_name in os.listdir(base_folder):
        folder_path = os.path.join(base_folder, folder_name)

        if os.path.isdir(folder_path):
            files = [file for file in os.listdir(
                folder_path) if os.path.isfile(os.path.join(folder_path, file))]
            folder = {
                'id': folder_path,
                'name': folder_name,
                'files': files,
                'owner': not os.path.islink(folder_path)
            }
            folders.append(folder)

    return folders


def get_file_from_folder(folder_name: str, file_name: str, user_name: str) -> str:
    """Retrieves the content of a file from the specified folder."""
    try:
        file_path = __get_file_path(user_name, folder_name, file_name)
        if os.path.exists(file_path):
            return file_path
    except Exception as e:
        print(f"Error reading file '{file_name}': {e}")


def create_folder(folder_name: str, user_name: str) -> None:
    """ Creates a new folder. """
    try:
        path = __get_folder_path(user_name, folder_name)
        os.makedirs(path, exist_ok=True)
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    except Exception as e:
        print(f"Error creating folder '{folder_name}': {e}")


def delete_folder(folder_name: str, user_name: str) -> None:
    """Deletes a folder and removes associated symlinks for shared users."""
    try:
        users_file = __get_file_path(user_name, folder_name, '.users')
        if os.path.exists(users_file):
            with open(users_file, 'r') as f:
                shared_users = [s for s in f.read().strip().split(',') if s]
            for shared_user in shared_users:
                shared_user_symlink = __get_folder_path(shared_user, folder_name)
                if os.path.exists(shared_user_symlink) and os.path.islink(shared_user_symlink):
                    os.unlink(shared_user_symlink)
        
        folder_path = __get_folder_path(user_name, folder_name)
        shutil.rmtree(folder_path)
    except Exception as e:
        print(f"Error deleting folder '{folder_name}': {e}")


def get_folder_content(folder_name: str, user_name: str) -> List[list]:
    """ Returns info about the content of a folder. """
    try:
        folder_path = __get_folder_path(user_name, folder_name)
        files = [f for f in os.listdir(folder_path) if os.path.isfile(
            os.path.join(folder_path, f)) and f != '.users']

        file_objects = []
        for file in files:
            file_path = os.path.join(folder_path, file)

            file_size_bytes = os.path.getsize(file_path)
            file_size_mb = file_size_bytes / (1024 * 1024)
            if file_size_mb < 1:
                file_size_kb = file_size_bytes / 1024
                size = f"{round(file_size_kb, 2)} Kb"
            else:
                size = f"{round(file_size_mb, 2)} Mb"

            creation_time = time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(os.path.getctime(file_path)))

            file_objects.append({
                'name': file,
                'size': size,
                'created_at': creation_time
            })

        return file_objects
    except Exception as e:
        print(f"Error listing files in folder '{folder_path}': {e}")
        return []


def add_file_to_folder(config: FileConfigSchema, user: str) -> str:
    """ Stores a file in folder. """
    try:
        if not os.path.exists(config.folder):
            os.makedirs(config.folder)

        file_path = __get_file_path(user, config.folder, config.name)
        file_name_without_ext, file_extension = os.path.splitext(config.name)
        counter = 1
        while os.path.exists(file_path):
            file_name = f"{file_name_without_ext}_{counter}{file_extension}"
            file_path = __get_file_path(user, config.folder, file_name)
            counter += 1

        with open(file_path, 'w') as file:
            file.write(config.content)
    except Exception as e:
        print(f"Error creating file '{config['name']}': {e}")


def delete_file(folder_name: str, file_name: str, user: str) -> str:
    """ Deletes a file from a folder. """
    try:
        file_path = __get_file_path(user, folder_name, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error deleting file '{file_name}': {e}")


def share_folder(folder_name: str, sender: str, receiver: str) -> None:
    """ Shares a folder with a user. """
    try:
        users_file = __get_file_path(sender, folder_name, '.users')      
        if not os.path.exists(users_file):
            with open(users_file, 'w') as file:
                file.write(receiver)
        else:
            with open(users_file, 'r') as f:
                shared_users = f.read().strip().split(',')
            if receiver not in shared_users:
                shared_users.append(receiver)
                with open(users_file, 'w') as f:
                    f.write(','.join(shared_users))

        receiver_folder = __get_user_folders_path(receiver)
        if not os.path.exists(receiver_folder):
            os.makedirs(receiver_folder)

        symlink_path = __get_folder_path(receiver, folder_name)
        if os.path.exists(symlink_path):
            raise FileExistsError(
                f"A folder with the name '{folder_name}' already exists.")

        shared_folder_path = __get_folder_path(sender, folder_name) 
        os.symlink(shared_folder_path, symlink_path)

    except Exception as e:
        print(f"Error creating symlink for folder '{folder_name}': {e}")

def unshare_folder(folder_name: str, sender: str, receiver: str) -> None:
    """ Unshares a folder with a user. """
    try:
        users_file = __get_file_path(sender, folder_name, '.users')
        if not os.path.exists(users_file):
            with open(users_file, 'w') as file:
                file.write('')
        else:
            with open(users_file, 'r') as f:
                shared_users = f.read().strip().split(',')
            if len(shared_users) == 1:
                with open(users_file, 'w') as f:
                    f.write('')
            elif receiver in shared_users:
                shared_users.remove(receiver)
                with open(users_file, 'w') as f:
                    f.write(','.join(shared_users))

        symlink_path = __get_folder_path(receiver, folder_name)
        if os.path.islink(symlink_path):
            os.unlink(symlink_path)
        else:
            raise FileNotFoundError(
                f"No symlink found for '{folder_name}' in the receiver's folder.")
    except Exception as e:
        print(f"Error unsharing folder '{folder_name}': {e}")


def get_folder_users(folder_name: str, user: str) -> List[str]:
    """ Returns the users of a folder. """
    try:
        folder_path = __get_folder_path(user, folder_name)
        if not os.path.exists(folder_path):
            raise FileNotFoundError(
                f"The folder '{folder_name}' does not exist.")

        users_file = __get_file_path(user, folder_name, '.users')
        shared_users = [user.get('email')]
        if os.path.exists(users_file):
            with open(users_file, 'r') as f:
                shared_users.extend(f.read().strip().split(',')) 
        return [s for s in shared_users if s]
    except Exception as e:
        print(f"Error creating symlink for folder '{folder_name}': {e}")
