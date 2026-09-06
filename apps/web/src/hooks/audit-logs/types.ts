export type AuditEventType =
  | 'PRODUCT_CREATED'
  | 'PRODUCT_UPDATED'
  | 'PRODUCT_DELETED'
  | 'ORDER_CREATED'
  | 'ORDER_UPDATED'
  | 'ORDER_DELETED'
  | 'STOCK_MOVEMENT'

export type AuditEntityType = 'PRODUCT' | 'ORDER'

export interface AuditLog {
  id: number
  event_type: AuditEventType
  entity_type: AuditEntityType
  entity_id: number
  details: Record<string, unknown>
  created_at: string
}
