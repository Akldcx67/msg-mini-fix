#include <string>
#include <iostream>
#include <stdlib.h>
#include <fstream>


using namespace std;


#ifdef _WIN32
    #include <windows.h>
#else
    #include <cstdlib>
#endif


const string python_libraries[] = {"flask", "bcrypt", "uuid"};
const string data_files[] = {"channels.json", "chats.json",
    "db.json", "keys.json",
    "users.json"};
const string back_files[] = {"main.py", "./modules/constants.py", "./modules/encryption.py", 
    "./modules/gambling.py", "./modules/keygen.py", 
    "./modules/loc_io.py"};
const string front_files[] = {"./templates/channel_list.html", "./templates/channel_settings.html", 
    "./templates/channel.html", "./templates/chat_list.html", 
    "./templates/chat_settings.html", "./templates/chat.html", 
    "./templates/create_channel.html", "./templates/create_chat.html", 
    "./templates/dm.html", "./templates/edit_profile.html", 
    "./templates/form.html", "./templates/login.html", 
    "./templates/main_no_user.html", "./templates/main.html", 
    "./templates/register.html", "./templates/user_profile.html", 
    "./templates/users.html"};


int checkLibraries(string flag) {
    for (string lib : python_libraries) {
        string command;
        if (flag == "none"){
            #ifdef _WIN32
                command = "pip install " + lib + " > nul 2>&1";
            #else
                command = "pip install " + lib + " > /dev/null 2>&1";
            #endif
        }
        else {
            #ifdef _WIN32
                command = "pip install " + lib + " " + flag + " > nul 2>&1";
            #else
                command = "pip install " + lib + " " + flag + " > /dev/null 2>&1";
            #endif
        }
        cout << "Checking for " << lib << " ..." << endl;
        int result = system(command.c_str());
        switch (result) {
        case 0:
            cout << lib << " installed." << endl;
            break;
        default:
            #ifdef _WIN32
                cout << "Unknown error, aborting" << endl;
                exit(1);
                return 1;
            #else
                if (flag == "none") {
                    cout << "Error" << endl;
                    cout << "Retry with flag --break-system-packages? [Y/N]";
                    char ans;
                    cin >> ans;
                    if (ans == 'Y' || ans == 'y') {
                        return 2;
                    }
                }
                else {
                    cout << "Unknown error" << endl;
                    exit(1);
                }
            #endif
            break;
        }
    }
    return 0;
}


int checkPython() {
    string command;
    #ifdef _WIN32
        command = "python -h > nul 2>&1";
    #else
        command = "python -h > /dev/null 2>&1";
    #endif
    int res = system(command.c_str());
    return res;
}


bool checkFileExists(const string& filename) {
    fstream file(filename, ios::in);
    return file.good();
}


int checkFilesystem() {
    cout << "Checking data files..." << endl;
    for (string filename : data_files) {
        if (!checkFileExists(filename)) {
            cout << filename << " does not exist, creating..." << endl;
            ofstream file(filename);
            file.close();
            cout << filename << " created" << endl;
        }
    }
    cout << "Checking backend files..." << endl;
    for (string filename : back_files) {
        if (!checkFileExists(filename)) {
            cout << "Backend file " << filename << " does not exist, continue?[Y/N]";
            char ans;
            cin >> ans;
            if (ans == 'N' || ans == 'n') {
                cout << "Aborting" << endl;
                return 1;
            }
        }
    }
    cout << "Checking frontend files..." << endl;
    for (string filename : front_files) {
        if (!checkFileExists(filename)) {
            cout << "Frontend file " << filename << " does not exist, continue?[Y/N]";
            char ans;
            cin >> ans;
            if (ans == 'N' || ans == 'n') {
                cout << "Aborting" << endl;
                return 1;
            }
        }
    }
    return 0;
}


int installLinux() {
    if (checkFileExists("/usr/bin/cosmicm/main.py") || checkFileExists("/usr/bin/cosmicm")) {
        cout << "Programm exist, do you want to update? (database files do not be deleted)[Y/N]";
        char ans;
        cin >> ans;
        if (ans == 'Y' || ans == 'y') {
            int check = system("rm /usr/bin/cosmicm/main.py > /dev/null 2>&1");
            if (check != 0) {
                cout << "Run configure as root!" << endl;
                return 1;
            }
            system("find /usr/bin/cosmicm -not -name '*.json' -not -path '.' -delete");
            for (string filename : back_files) {
                string command = "cp " + filename + " /usr/bin/cosmicm/" + filename + " > /dev/null 2>&1";
                system(command.c_str());
            }
            for (string filename : front_files) {
                string command = "cp " + filename + " /usr/bin/cosmicm/" + filename + " > /dev/null 2>&1";
                system(command.c_str());
            }
            cout << "Update finished!" << endl;
        }
        return 0;
    }
    cout << "Do you want to install cosmicm to /usr/bin ?[Y/N]";
    char ans;
    cin >> ans;
    if (ans == 'Y' || ans == 'y') {
        int check = system("mkdir /usr/bin/cosmicm > /dev/null 2>&1");
        if (check != 0) {
            cout << "Run configure as root!" << endl;
            return 1;
        }
        system("mkdir /usr/bin/cosmicm/modules > /dev/null 2>&1");
        system("mkdir /usr/bin/cosmicm/templates > /dev/null 2>&1");
        cout << "Copying data files..." << endl;
        for (string filename : data_files) {
            string command = "cp " + filename + " /usr/bin/cosmicm/ > /dev/null 2>&1";
            system(command.c_str());
        }
        cout << "Copying backend files..." << endl;
        for (string filename : back_files) {
            string command = "cp " + filename + " /usr/bin/cosmicm/" + filename + " > /dev/null 2>&1";
            system(command.c_str());
        }
        cout << "Copying frontend files..." << endl;
        for (string filename : front_files) {
            string command = "cp " + filename + " /usr/bin/cosmicm/" + filename + " > /dev/null 2>&1";
            system(command.c_str());
        }
        cout << "Copying run script..." << endl;
        ofstream run_script("/usr/bin/cosmic");
        run_script << "#!/bin/bash\ncd /usr/bin/cosmicm\npython /usr/bin/cosmicm/main.py";
        run_script.close();
        system("chmod +x /usr/bin/cosmic");
        cout << "Cosmic installed!" << endl;
    }
    return 0;
}


int main (int argc, char *argv[]) {
    cout << "Checking for python..." << endl;
    switch (checkPython()) {
    case 0:
        cout << "Python exist" << endl;
        break;
    default:
        cout << "Cannot find python, aborting" << endl;
        exit(1);
        return 1;
        break;
    }
    cout << "Cheking for python dependencies..." << endl;
    switch (checkLibraries("none")) {
    case 2:
        checkLibraries("--break-system-packages");
        cout << "All libraries installed, good" << endl;
        break;
    default:
        cout << "All libraries installed, good" << endl;
        break;
    }
    cout << "Checking filesystem..." << endl;
    switch (checkFilesystem()) {
    case 0:
        cout << "Filesystem checked" << endl;
        break;
    default:
        cout << "Aborting" << endl;
        exit(1);
        return 1;
        break;
    }
    #ifdef _WIN32
    #else
        installLinux();
    #endif
    cout << "All done!" << endl;
    return 0;
}
