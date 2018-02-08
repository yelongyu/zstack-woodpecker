package main

import (
        "fmt"
        "net/http"
	"github.com/gorilla/mux"
        "sync"
        "sort"
)

var vcenter []string;
var lastvcenter string;

type Set struct {
	m map[string]bool
	sync.RWMutex
}

func New() *Set {
	return &Set{
		m: map[string]bool{},
	}
}

func (s *Set) AddVcenterCandidate(w http.ResponseWriter, r *http.Request) {
        params := mux.Vars(r)
        new_vcenter := params["vc"]
	s.Lock()
	defer s.Unlock()
	s.m[new_vcenter] = true
}

func (s *Set) DeleteVcenterCandidate(w http.ResponseWriter, r *http.Request) {
        params := mux.Vars(r)
        vc := params["vc"]
        lastvcenter = params["vc"]
	s.Lock()
	defer s.Unlock()
	delete(s.m, vc)
}

func (s *Set) Has(w http.ResponseWriter, r *http.Request) bool {
        params := mux.Vars(r)
        vc := params["vc"]
	s.RLock()
	defer s.RUnlock()
	_, ok := s.m[vc]
	return ok
}

func (s *Set) GetVcenter(w http.ResponseWriter, r *http.Request) {
	s.RLock()
	defer s.RUnlock()
	list := []string{}
	for item := range s.m {
		list = append(list, item)
	}
	sort.Strings(list)
        if len(list) == 0 {
                fmt.Fprintln(w, "No available vcenter")
        } else {
                fmt.Fprintln(w, list[0])
        }
}

func (s *Set) GetAllVcenter(w http.ResponseWriter, r *http.Request) {
        s.RLock()
        defer s.RUnlock()
        list := []string{}
        for item := range s.m {
                list = append(list, item)
        }
        sort.Strings(list)
        if len(list) == 0 {
                fmt.Fprintln(w, "No available vcenter")
        } else {
                fmt.Fprintln(w, list)
        }
}

func (s *Set) GetLastVcenter(w http.ResponseWriter, r *http.Request) {
        s.RLock()
        defer s.RUnlock()
        fmt.Fprintln(w, lastvcenter)
}

func main() {
	s := New()

        router := mux.NewRouter().StrictSlash(true)
        router.HandleFunc("/vcenter", s.GetVcenter).Methods("GET")
        router.HandleFunc("/all", s.GetAllVcenter).Methods("GET")
        router.HandleFunc("/lastvcenter", s.GetLastVcenter).Methods("GET")
        router.HandleFunc("/vcenter/{vc}", s.AddVcenterCandidate).Methods("PUT")
        router.HandleFunc("/vcenter/{vc}", s.DeleteVcenterCandidate).Methods("DELETE")

        http.ListenAndServe(":8080", router)
}
