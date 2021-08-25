#ifndef PARSER_H
#define PARSER_H
void getVariables(
    std::string& filename, 
    time_t& stored_mod_time, 
    std::vector<double>& variables);
bool doesFileExist(const std::string& name);
time_t getModTime(std::string& filename);
bool hasFileChanged(std::string& filename, time_t& stored_mod_time);
std::vector<double> parseFile(std::string& filename);
#endif 