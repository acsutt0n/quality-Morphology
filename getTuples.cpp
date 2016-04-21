// Push a list of tuples to check the intensity of pixels
// A tuple is <x,y,z>

// Requires -std=c++11

#include <iostream>
#include <vector>
#include <fstream>
#include <string>
#include <sstream>
#include <iterator>


using namespace std;


// Get the nodes and number of nodes
class Nodes 
{
  const char filename;
  public:
    int numNodes = 0;
    // id, x, y, z, time(ms), intensity    length=6
    std::vector<tuple<int, int, int, int, int, int>> nodeList;
    Nodes (const char filename); // Construct the class
    void getTuples(void); // Iterate through the file and get the tuples
    void addTuple(std::string);
    void write_file(const char* outname);
};



// Constructor: set the filename
/*
Nodes::Nodes (const char fname) 
{
  filename = fname;
}
*/

////////////////////////////////////////////////////////////////////////
// getTuples and helpers

// parse line for target sequence
bool contains_regex(std::string line, const char* pattern) {
  bool found = false;
  int offset;
  // If 'pattern' is found in the line before end of line
  if (line.find(pattern, 0) != string::npos) {
    found = true;
  }
  return found;
}



// stringsplit -- overloaded to allow for appending or creating a new vec
std::vector<std::string> &split(const std::string &s,
                                const char* delim,
                                std::vector<std::string> &elems) {
  std::stringstream ss(s);
  std::string item;
  while (std::getline(ss, item, delim)) {
    elems.push_back(item);
  }
  return elems;
}


std::vector<std::string> split(const std::string &s, const char* delim) {
  std::vector<std::string> elems;
  split(s, delim, elems);
  return elems;
}


// Test the string splitter
void test_split(const std::string &s, const char* delim) {
  std::vector<std::string> elems = split(s, delim);
  for (std::vector<std::string>::iterator it = elems.begin(); it != elems.end(); ++it) {
    std::cout << *it << " ";
  }
}


// addTuple -- add the tuple from a contains_regex+ line to the class
void Nodes::addTuple(std::string line) {
  const char* delim = "\"";
  std::vector<std::string> elems = split(line, delim);
  // <node id="1" radius="1.5" x="4" y="9" z="6" inVp="0" inMag="1" time="243215762"/>
  //      0    1    2       3  4  5  6  7  8  9  10    11  12   13  14     15       16
  int id   = std::stoi(elems[1]);
  int x    = std::stoi(elems[5]);
  int y    = std::stoi(elems[7]);
  int z    = std::stoi(elems[9]);
  int time = std::stoi(elems[15]);
  int intensity = 0;
  //
  std::vector<int> temp_vec;
  temp_vec.push_back(id);
  temp_vec.push_back(x);
  temp_vec.push_back(y);
  temp_vec.push_back(z);
  temp_vec.push_back(time);
  temp_vec.push_back(intensity); // done.
  nodeList.push_back(temp_vec);
}



// getTuples -- get the tuples from the file
void Nodes::getTuples(void) {
  std::ifstream infile = filename;
  std::string line;
  const char* pattern = "node id";
  while (std::getline(infile, line)) {
    bool found = false;
    found = contains_regex(line, pattern);
    // If the pattern was found, there is a node in this line; find tuple
    if (found) {
      addTuple(line);
      numNodes++; // Increment node number
    }
  }
  // Should now have all the tupes in the file
}



////////////////////////////////////////////////////////////////////////
// Output options

void Nodes::write_file(const char* outname) {
  //
}




////////////////////////////////////////////////////////////////////////
// Testing

int main()
{
  // 
  
  //
  
  // Testing string split
  std::string bat = "I'd\"rather\"date\"a\"spider\"or\"a\"bat";
  const char* delim = "\"";
  test_split(bat, delim);
}














