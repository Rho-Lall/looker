view: customer_orders {
  sql_table_name: `warehouse.raw.customer_orders` ;;

  dimension: order_id {
    type: string
    sql: ${TABLE}.order_id ;;
  }

  dimension: customer_id {
    type: string
    sql: ${TABLE}.customer_id ;;
  }

  dimension: product_id {
    type: string
    sql: ${TABLE}.product_id ;;
  }

  dimension: order_amount {
    type: number
    sql: ${TABLE}.order_amount ;;
  }

  dimension: tax_amount {
    type: number
    sql: ${TABLE}.tax_amount ;;
  }

  dimension: discount_amount {
    type: number
    sql: ${TABLE}.discount_amount ;;
  }

  dimension: shipping_cost {
    type: number
    sql: ${TABLE}.shipping_cost ;;
  }

  dimension: customer_name {
    type: string
    sql: ${TABLE}.customer_name ;;
  }

  dimension: product_category {
    type: string
    sql: ${TABLE}.product_category ;;
  }

  dimension: order_status {
    type: string
    sql: ${TABLE}.order_status ;;
  }

  dimension: payment_method {
    type: string
    sql: ${TABLE}.payment_method ;;
  }

  dimension: is_gift_order {
    type: yesno
    sql: ${TABLE}.is_gift_order ;;
  }

  dimension: is_express_shipping {
    type: yesno
    sql: ${TABLE}.is_express_shipping ;;
  }

  dimension_group: order_date {
    type: time
    timeframes: [
      raw,
      time,
      date,
      week,
      month,
      quarter,
      year
    ]
    sql: ${TABLE}.order_date ;;
  }

  dimension_group: shipped_date {
    type: time
    timeframes: [
      raw,
      date,
      week,
      month
    ]
    sql: ${TABLE}.shipped_date ;;
  }

  measure: count {
    type: count
    drill_fields: [order_id, customer_name]
  }
}