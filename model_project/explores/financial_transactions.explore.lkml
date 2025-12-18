explore: financial_transactions {
  join: customers {
    type: left_outer
    relationship: many_to_one
    sql_on: ${financial_transactions.customer_id} = ${customers.customer_id} ;;
  }

}