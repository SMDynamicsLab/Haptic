#include<iostream>
#include<string>
#include<fstream>

#include <sys/types.h>
#include <sys/stat.h>

#include <vector>

#include "parser.h"
using namespace std;

bool getVariables(
    string& filename, 
    time_t& stored_mod_time, 
    vector<double>& variables
)
{
    if(doesFileExist(filename) &&  hasFileChanged(filename, stored_mod_time)){
        cout << "C++: Reading input file" << endl;
        variables = parseFile(filename);
        stored_mod_time = getModTime(filename); //store last modification date
    }
    else if (!doesFileExist(filename))
    {
        cout << "C++: Input file does not exist (anymore)" << endl;
        return 0;
    }
    return 1;
}

bool doesFileExist(const string& name)
{
    if (FILE *file = fopen(name.c_str(), "r")) {
        fclose(file);
        return true;
    } else {
        return false;
    }   
}

time_t getModTime(string& filename)
{
    struct stat result;
    if(stat(filename.c_str(), &result)==0)
        {
            time_t mod_time = result.st_mtime; //epoch
            return mod_time;
        }
}

bool hasFileChanged(string& filename, time_t& stored_mod_time)
{
    return getModTime(filename) != stored_mod_time;
}

vector<double> parseFile(string& filename)
{   
    vector<double> vars;
    ifstream ifile(filename, ios::in);
    double num = 0.0;

    //check to see that the file was opened correctly:
    if (!ifile.is_open()) {
        cerr << "There was a problem opening the input file!\n";
        exit(1);//exit or do additional error checking
    }

    //keep storing values from the text file so long as data exists:
    while (ifile >> num) {
        vars.push_back(num);
    }

    // Print out the vector
    std::cout << "C++: variables = ( ";
    for (double n : vars) {
        std::cout << n << ", ";
    }
    std::cout << ")" << endl;

    return vars;
}

void appendToCsv(
    string& output, 
    vector<vector<double>>& data, 
    int& trialCounter,
    vector<double>& variables,
    bool& trialSuccess
)
{   
    cout<<"C++: Appending data to file for trial " << trialCounter<< endl;
    ofstream fout;
    fout.open(output, ios::app); // Append mode
    if(fout.is_open()){
        for (auto & row : data)
        {   
            fout<< trialCounter; 
            fout<< ",";
            for (auto & value : row) {
                fout<< value;
                fout<< ",";
            }
            for (auto & value : variables) {
                fout<< value;
                fout<< ",";
            }
            fout<< trialSuccess;             
            fout<< "\n";    
        }
        cout<<"C++: Data has been appended to file for trial " << trialCounter<< endl;        
    }
    else{
        cout<<"C++: Output file not opened correctly"<< endl;
    }
    fout.close();
    cout<<"C++: Output file closed" << trialCounter<< endl;
    
}