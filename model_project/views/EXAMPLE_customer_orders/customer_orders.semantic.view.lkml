include: "customer_orders.source.view"

view: +customer_orders {

  # IDs

  dimension: order_id {
    primary_key: yes
  }

  dimension: customer_id {
    primary_key: yes
  }

  dimension: product_id {
  }

  # METRICS

  measure: order_amount_total {
    type: sum
    sql: ${order_amount};;
  }

  measure: tax_amount_total {
    type: sum
    sql: ${tax_amount};;
  }

  measure: discount_amount_total {
    type: sum
    sql: ${discount_amount};;
  }

  measure: shipping_cost_total {
    type: sum
    sql: ${shipping_cost};;
  }

}