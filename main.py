import asyncio
from pathlib import Path

from config import config
from database import initialize_db, close_db
from notifications import send_email_message
from olimp_loader.olimp_loader import OlimpLoader
from unziper.unziper import Unziper


async def main():
    initialize_db()
    while True:
        try:
            olimp_loader = OlimpLoader()
            try:
                await olimp_loader.init(
                    login=config.mayak_config.login,
                    password=config.mayak_config.password.get_secret_value(),
                )
                while True:
                    current_files = await olimp_loader.look_for_olimp_files(
                        table_name="Форма публикации списков распределённых в МПО и сбора сведений о ходе проведения РЭ ВсОШ 2025 - 2026 учебного года")
                    new_files = await olimp_loader.get_new_olimp_files(current_files)
                    for new_file in new_files:
                        students_list_path = await olimp_loader.download_olimp_file(new_file.students_list_link,
                                                                                    config.storage.folder_path)
                        students_list_target_path = Path(students_list_path)
                    #     Unziper().unzip_file(path=Path(students_list_path), target_path=students_list_target_path)
                    #     for file in students_list_target_path.glob("*"):
                        await send_email_message(
                            subject=f"Олимпиада {new_file.date} {new_file.subject} ",
                            message_text=f"<strong>Получены новые списки участников из ЕКИС.</strong>",
                            file_path=Path(students_list_path),
                            sender_email=config.email.smtp_login,
                            sender_password=config.email.smtp_password.get_secret_value(),
                            receiver_emails=config.email.target_emails,
                            smtp_server_hostname=config.email.smtp_server,
                            smtp_server_port=config.email.smtp_port
                        )
                    #         protocols_path = await olimp_loader.download_olimp_file(new_file.protocols_link,
                    #                                                                 config.storage.folder_path)
                    #         await send_email_message(
                    #             subject=f"Олимпиада {new_file.date} {new_file.classes} {new_file.subject}",
                    #             message_text=f"<strong>Получены новые протоколы олимпиады из ЕКИС.<br>Классы участия: {new_file.classes}</strong>",
                    #             file_path=Path(protocols_path),
                    #             sender_email=config.email.smtp_login,
                    #             sender_password=config.email.smtp_password.get_secret_value(),
                    #             receiver_emails=config.email.target_emails,
                    #             smtp_server_hostname=config.email.smtp_server,
                    #             smtp_server_port=config.email.smtp_port
                    #         )
                    # current_files = await olimp_loader.look_for_olimp_files(
                    #     table_name="Информация об учащихся, приглашённых на муниципальный этап ВсОШ 2025-2026 уч. года")
                    # new_files = await olimp_loader.get_new_olimp_files(current_files)
                    # for new_file in new_files:
                    #     students_list_path = await olimp_loader.download_olimp_file(new_file.students_list_link,
                    #                                                                 config.storage.folder_path)
                    #     students_list_target_path = Path(students_list_path.strip(".zip"))
                    #     Unziper().unzip_file(path=Path(students_list_path), target_path=students_list_target_path)
                    #     for file in students_list_target_path.glob("*"):
                    #         await send_email_message(
                    #             subject=f"Олимпиада {new_file.date} {new_file.classes} {new_file.subject} ",
                    #             message_text=f"<strong>Получены новые списки приглашенных из ЕКИС.<br>Классы участия: {new_file.classes}</strong>",
                    #             file_path=Path(file),
                    #             sender_email=config.email.smtp_login,
                    #             sender_password=config.email.smtp_password.get_secret_value(),
                    #             receiver_emails=config.email.target_emails,
                    #             smtp_server_hostname=config.email.smtp_server,
                    #             smtp_server_port=config.email.smtp_port
                    #         )

                    await asyncio.sleep(1)
            except Exception as e:
                print(e)
                await olimp_loader.close()
        except Exception as e:
            print(e)
            close_db()


if __name__ == '__main__':
    asyncio.run(main())
