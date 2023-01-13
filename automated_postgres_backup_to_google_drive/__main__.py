import os
import yaml
import subprocess
from packages.gdrive import gdrive
from packages.logger import logger
from packages.project import absolute_path
from packages.timestamp import timestamp
from packages.mail import mail


# Initiate logger
project_abs_path = os.path.dirname(absolute_path.get())
logs_file_path = logger.create_log_file(
    app_name='automated_postgres_backup_to_google_drive',
    project_abs_path=project_abs_path
)
log = logger.setup_app_logger(logger_name='', log_file_path=logs_file_path)


def main():

    try:

        log.info('Start program execution')

        # Import configurations
        config_path = os.path.join(absolute_path.get(), 'config.yaml')
        with open(config_path) as config_file:
            config = yaml.safe_load(config_file)
        log.info('Imported configurations successfully')

        # **************** Create the backup of the database **************** #

        # Set the name of the backup file
        bkup_filename = config['database']['bkup_name'] + '_' + \
            timestamp.get_current(format='%d-%m-%Y__%H-%M-%S') + '.sql'

        # Set the path of the backup folder
        bkup_folder = os.path.join(absolute_path.get(), 'data/output/')

        # Set the full path to the backup file
        bkup_path = os.path.join(bkup_folder, bkup_filename)

        # Set the full command of creating a backup of the database
        bkup_cmd = 'PGPASSWORD="{0}" pg_dump -h localhost -U {1} -F p {2} > {3}' \
            .format(config['database']['password'], config['database']['user'],
                    config['database']['database_name'], bkup_path)

        # Execute the command to create the backup of the database
        subprocess.check_output(bkup_cmd, shell=True)

        log.info('Finished creating a backup of the database')

        # **************** Upload the backup to Google Drive **************** #

        # Create an object from GoolgeDrive class
        key_path = os.path.join(
            absolute_path.get(),
            'data/input/google_drive_service_account_key.json'
        )
        drive = gdrive.GoogleDrive(key_file_location=key_path)

        # Upload the backup filee to the remote folder
        drive.upload_file(
            file_name=bkup_filename,
            folder_path=bkup_folder,
            remote_folder_name=config['drive']['folder_name']
        )

        log.info('Finished uploading the backup to google drive')

        # ***************** Delete the local file ***************** #

        os.remove(bkup_path)
        log.info('Finished deleting the local backup file ')

        # Set a flag to indicate that there wasn't any errors
        is_error = False
        error_message = None

    except Exception as e:

        # Set a flag to indicate that there was an error
        is_error = True
        error_message = str(e)

        log.error('Error while executing the main function: {0}'.format(e))

    # ***************** Send the Report Mail ***************** #

    try:

        smtp_dict = {
            'sender': config['smtp']['sender'],
            'password': config['smtp']['password'],
            'sender_title': config['smtp']['sender_title'],
            'hostname': config['smtp']['hostname'],
            'port': config['smtp']['port'],
        }

        mail_dict = {
            'recipients': ['muhammadabdelgawwad@gmail.com', ],
            'cc': [],
            'attachments': [],
        }

        # Set the mail body
        if not is_error:
            mail_dict['subject'] = 'Database Daily Backup Report'
            mail_template_path = os.path.join(
                absolute_path.get(), 'data/input/mail_template.html'
            )
            with open(mail_template_path, "r", encoding='utf-8') as f:
                mail_body = f.read()

        else:
            mail_dict['subject'] = 'Error | Database Daily Backup Report'
            mail_template_path = os.path.join(
                absolute_path.get(), 'data/input/error_mail_template.html'
            )
            with open(mail_template_path, "r", encoding='utf-8') as f:
                mail_body = f.read().replace(
                    '{{ ErrorMessage }}', error_message
                )

        mail_dict['message'] = mail_body

        mail.send(smtp_dict, mail_dict)

        log.info('Finished sending the mail successfully')

        log.info('Finished program execution')

    except Exception as e:
        log.error('Error while sending the mail report: {0}'.format(e))


if __name__ == '__main__':
    main()
