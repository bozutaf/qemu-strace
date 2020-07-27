import os, sys
import CppHeaderParser

available_targets = ['aarch64','aarch64_be', 'alpha','armeb','avr','cris',
                     'hppa','i386','m68k','microblaze','microblazeel',
                     'mips','mips64','mips64el','mipsel','mipsn32','mipsn32el'
                     'nios2','or1k','ppc','ppc64','ppc64abi32''ppc64le',
                     'riscv32','riscv64','s390x','sh4','sh4eb','sparc',
                     'sparc32plus','sparc64','tilegx''x86_64','xtensa',
                     'xtensaeb']

syscall_nr_path = "-linux-user/linux-user/"
#syscall_nr_file

# case when the target is specified as a command line argument
if len(sys.argv) > 1:

    # check if QEMU is compiled for the specified target
    if os.path.isdir(target + "-linux-user/"):
        # generate the path to 'syscall_nr.h' header file
        syscall_nr_path = "../" + sys.argv[1] + syscall_nr_path + \
                          sys.argv[1] + "/syscall_nr.h"

        # attempt to parse the 'syscall_nr.h' file
        try:
            syscall_nr_file = CppHeaderParser.CppHeader(syscall_nr_path)
        # if for some reason parsing of the 'syscall_nr.h' file fails
        except CppHeaderParser.CppParseError as e:
            print("Failed to open file: " + sys.argv[1] + 'syscall_nr.h');
            print(e)
            sys.exit(1)

    else:
        print(sys.argv[1] + "-linux-user: Folder doesn't exist!")
        print("QEMU not compiled for target: " + sys.argv[1] + "-linux-user")
        sys.exit(1)

# if the target is not specified, find the first available target
else:
    syscall_nr_file_opened = False

    for target in available_targets:
        # available target found
        if os.path.isdir("../" + target + "-linux-user/"):
            # generate the path to 'syscall_nr.h' header file
            syscall_nr_path = "../" + target + syscall_nr_path + \
                              target + "/syscall_nr.h"

            # attempt to parse the 'syscall_nr.h' file
            try:
                syscall_nr_file = CppHeaderParser.CppHeader(syscall_nr_path)
            # if for some reason parsing of the 'syscall_nr.h' file fails
            except CppHeaderParser.CppParseError as e:
                print("Failed to open file: " + target + 'syscall_nr.h');
                print(e)
                # continue to next available target
                continue

            syscall_nr_file_opened = True
            break

    if syscall_nr_file_opened == False:
        print("Couldn't open any 'syscall_nr.h' file")
        print("Check if QEMU is compiled for any linux-user target")
        sys.exit(1)

# array that contains string representations of syscall
# target numbers
syscall_targets = []

for define in syscall_nr_file.defines:
    if define.startswith("TARGET_NR_"):
        syscall_targets.append(define.split('\t')[0])

strace_entries = {}
strace_entry = {}

try:
    strace_file = open("../linux-user/strace.list")
except IOError:
    print("'strace.list' file not found")
    sys.exit(1)

line = strace_file.readline()

while line:
    if line.startswith("{"):
        strace_data = line.replace('{', '');
        strace_data = line.replace('}', '');
        strace_data = strace_data.split(',');

        strace_entry['syscall_target'] = strace_data[0];
        strace_entry['syscall_name'] = strace_data[1];
        strace_entry['print_format'] = strace_data[2];
        strace_entry['print_function'] = strace_data[3];
        strace_entry['print_ret_function'] = strace_data[4];

        strace_entries[strace_data[0]] = strace_entry;

    line = strace_file.readline()
