// derivative_pricer.cpp  ----------------------------------------------------
// One‑file workflow: BOTH the discount curve and one or more caplet rows
// live in a single CSV.  No flags required except the file name.
//
// CSV layout (example):
// -------------------------------------------------
// maturity,zero_rate
// 0.5,0.03
// 1,0.032
// 2,0.035
// 5,0.04
// 10,0.042
//
// T,F,K,sigma,tau   # <‑‑ header marks start of caplet block
// 2,0.037,0.04,0.25,0.5
// 3,0.038,0.04,0.24,0.5
// -------------------------------------------------
// Build:
//    g++ -std=c++17 derivative_pricer.cpp -o pricer
// Run:
//    ./pricer market_data.csv
// ---------------------------------------------------------------------------

#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <iomanip>
#include <stdexcept>

// ---------------- std‑normal PDF & CDF ------------------------------------
constexpr double SQRT_2      = 1.4142135623730951;
constexpr double INV_SQRT2PI = 0.3989422804014327;
inline double n_pdf(double x){ return INV_SQRT2PI*std::exp(-0.5*x*x);}
inline double n_cdf(double x){ return 0.5*std::erfc(-x/SQRT_2);}

// ---------------- Basic structs -------------------------------------------
struct DiscCurve{ std::vector<double> t, df; double operator()(double T) const;};
struct Caplet   { double T,F,K,sigma,tau; };

double DiscCurve::operator()(double T) const{
    if(T<=t.front()) return df.front();
    if(T>=t.back())  return df.back();
    size_t i = std::upper_bound(t.begin(),t.end(),T)-t.begin()-1;
    double w = (T-t[i])/(t[i+1]-t[i]);
    return std::exp(std::log(df[i])+w*(std::log(df[i+1])-std::log(df[i])));
}

// ---------------- File loader ---------------------------------------------
void load_market_file(const std::string& file, DiscCurve& curve, std::vector<Caplet>& caps){
    std::ifstream fin(file);
    if(!fin) throw std::runtime_error("Cannot open file: "+file);
    std::string line; bool reading_curve=true;
    while(std::getline(fin,line)){
        if(line.empty()) continue;                      // skip blanks
        if(line[0]=='#') continue;                      // skip comments
        // detect second header → switch to caplets
        if(line.rfind("T",0)==0){ reading_curve=false; continue; }
        std::replace(line.begin(),line.end(),',',' ');
        std::istringstream ss(line);
        if(reading_curve){
            double m,z; ss>>m>>z;
            if(ss){ curve.t.push_back(m); curve.df.push_back(std::exp(-z*m)); }
        }else{
            Caplet c; ss>>c.T>>c.F>>c.K>>c.sigma>>c.tau;
            if(ss) caps.push_back(c);
        }
    }
    if(curve.t.size()<2) throw std::runtime_error("Curve section missing or too short");
    if(caps.empty())      throw std::runtime_error("Caplet section missing");
}

// ---------------- Black caplet pricer -------------------------------------
double price_caplet(const DiscCurve& curve,const Caplet& c){
    double sd=c.sigma*std::sqrt(c.T);
    double d1=(std::log(c.F/c.K)+0.5*sd*sd)/sd;
    double d2=d1-sd;
    double df=curve(c.T);
    return df*c.tau*(c.F*n_cdf(d1)-c.K*n_cdf(d2));
}
void greeks(const DiscCurve& curve,const Caplet& c,double& delta,double& vega){
    double sd=c.sigma*std::sqrt(c.T);
    double d1=(std::log(c.F/c.K)+0.5*sd*sd)/sd;
    double df=curve(c.T);
    delta=df*c.tau*n_cdf(d1);
    vega =df*c.tau*c.F*std::sqrt(c.T)*n_pdf(d1);
}

// ---------------- Main -----------------------------------------------------
int main(int argc,char**argv){
    if(argc!=2){ std::cerr<<"Usage: ./pricer market_data.csv\n"; return 1; }
    try{
        DiscCurve curve; std::vector<Caplet> caps;
        load_market_file(argv[1], curve, caps);
        std::cout<<"T,F,K,sigma,tau,Price,Delta,Vega\n";
        std::cout<<std::fixed<<std::setprecision(6);
        for(const auto& c:caps){
            double delta,vega; double px=price_caplet(curve,c); greeks(curve,c,delta,vega);
            std::cout<<c.T<<","<<c.F<<","<<c.K<<","<<c.sigma<<","<<c.tau
                     <<","<<px<<","<<delta<<","<<vega<<"\n";
        }
    }
    catch(const std::exception& e){ std::cerr<<"Error: "<<e.what()<<"\n"; return 1; }
    return 0;
}
