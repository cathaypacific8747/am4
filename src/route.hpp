int optimal_l_real_price(float distance);
int optimal_h_real_price(float distance);
int optimal_l_easy_price(float distance);
int optimal_h_easy_price(float distance);
int optimal_y_real_price(float distance);
int optimal_j_real_price(float distance);
int optimal_f_real_price(float distance);
int optimal_y_easy_price(float distance);
int optimal_j_easy_price(float distance);
int optimal_f_easy_price(float distance);

struct PaxTicket {
    int y_price;
    int j_price;
    int f_price;
};

struct CargoTicket {
    int l_price;
    int h_price;
};

PaxTicket create_pax_ticket(float distance, bool is_easy);
CargoTicket create_cargo_ticket(float distance, bool is_easy);