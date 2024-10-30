import os, time

class PrefetchChecker:
    def __init__(self, windir):
        self.windir = windir
        self.prefetch_dir = os.path.join(self.windir, "Prefetch")
        self.check_type = None

    def _get_prefetch_files(self):
        prefetch_files = os.listdir(self.prefetch_dir)
        filepaths = []
        for pf_file in prefetch_files:
            if pf_file[-2:] == "pf":
                full_path = self.prefetch_dir + '\\' + pf_file
                filepaths.append(full_path.lower())
        return filepaths

    def _read_program_list(self):
        program_list_file = input("Введите имя файла со списком программ (без расширения): ")
        program_list_file_path = os.path.join(os.getcwd(), program_list_file + '.txt')
        
        with open(program_list_file_path, 'r') as f:
            program_list = [line.strip().lower() for line in f if line.strip().endswith('.exe')]
        return program_list

    def _set_check_type(self):
        whitelist_mode = input("Выберите тип проверки: white | black ").lower()
        self.check_type = whitelist_mode
        if whitelist_mode not in ['white', 'black']:
            print("Неверный выбор. Используем белый список.")
            self.check_type = 'white'

    def _check_programs(self, program_list, prefetch_files):
        # Создаем множество для всех файлов
        all_files = set(prefetch_files)
        
        # Создаем множество для файлов, соответствующих программам
        matching_files = {program.lower(): set() for program in program_list}
        
        # Проходим по всем программам и создаем множества соответствующих файлов
        for program in program_list:
            program_lower = program.lower()
            matching_files[program_lower] = {
                file for file in all_files 
                if program_lower in file.lower()
            }
        
        # Инициализируем результат
        result = []
        # Безопасен ли ПК
        is_safe = True
        
        # Обрабатываем все файлы
        for file in all_files:
            program_lower = next((p for p in matching_files if p in file.lower()), None)
            
            last_executed = os.path.getmtime(file)
            last_executed = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_executed))
            
            status = 'clear'
            
            if self.check_type == 'black':
                if program_lower:
                    status = 'violation'
                else:
                    status = 'clear'
            elif self.check_type == 'white':
                if program_lower:
                    status = 'clear'
                else:
                    status = 'violation'
            
            result.append((file, last_executed, status))

            # Если найдено хотя бы одно нарушение, устанавливаем is_safe в False
            if status == 'violation':
                is_safe = False
        
        return result, is_safe

    def generate_output_table(self, checked_programs, is_safe):
        output = "| Наименование | Дата последнего запуска |\n"
        output += "|-------------|--------------------------|\n"
        for program, last_run, status in checked_programs:
            if status == "violation":
                output += f"| {program} | <b>{last_run}</b> |\n"
            else:
                output += f"| {program} | {last_run} |\n"

        # Добавляем информацию о безопасности ПК
        if is_safe:
            output += "\n| - | - | ПК считается безопасным. |\n"
        else:
            output += "\n| - | - | ПК считается небезопасным. |\n"

        return output

    def save_to_file(self, output, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(output)

    def run(self):
        # ['c:\\windows\\prefetch\\avp.exe-2f22b972.pf', 'c:\\windows\\prefetch\\chrome.exe-ccf9f3f5.pf']
        prefetch_files = self._get_prefetch_files()
        print(prefetch_files)
        #['chrome.exe']
        program_list = self._read_program_list()

        # Установка типа сравнения списков
        self._set_check_type()
        
        checked_programs, is_safe = self._check_programs(program_list, prefetch_files)
        
        output_table = self.generate_output_table(checked_programs, is_safe)

        print("\nРезультаты:")
        print(output_table)

        if is_safe:
            print("\nПК считается безопасным.")
        else:
            print("\nПК считается небезопасным.")
        
        self.save_to_file(output_table, "result.txt")
        
        print("\nРезультаты сохранены в файл result.txt")

if __name__ == "__main__":
    windir = os.environ['WINDIR'] if 'WINDIR' in os.environ else r'C:\Windows'
    checker = PrefetchChecker(windir)
    checker.run()