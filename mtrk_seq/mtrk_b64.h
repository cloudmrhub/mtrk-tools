#ifndef mtrk_b64_h
#define mtrk_b64_h 1

namespace SEQ_NAMESPACE
{ 

    class mtrk_b64 {
    public:
        static const std::string b64encode(const void* data, const size_t &len);
        static const std::string b64decode(const void* data, const size_t &len);
        static std::string b64encode(const std::string& str);
        static std::string b64decode(const std::string& str64);    
    };
}

#endif
