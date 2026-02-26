import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  users: defineTable({
    name: v.string(),
    role: v.union(
      v.literal("student"),
      v.literal("maintenance"),
      v.literal("supervisor")
    ),
    email: v.string(),
    assignedZones: v.array(v.string()),
  }).index("by_email", ["email"]),

  assets: defineTable({
    tagId: v.string(),
    name: v.string(),
    category: v.string(),
    location: v.string(),
    status: v.union(
      v.literal("healthy"),
      v.literal("watch"),
      v.literal("critical"),
      v.literal("offline")
    ),
    riskScore: v.number(),
    lastInspectionAt: v.number(),
    ownerTeam: v.string(),
    maintainerUserId: v.optional(v.id("users")),
    model: v.optional(v.string()),
    notes: v.optional(v.string()),
  })
    .index("by_tag", ["tagId"])
    .index("by_location", ["location"])
    .index("by_risk", ["riskScore"]),

  inspections: defineTable({
    assetId: v.id("assets"),
    reporterUserId: v.id("users"),
    source: v.union(v.literal("nfc_scan"), v.literal("manual")),
    note: v.string(),
    imageUrl: v.optional(v.string()),
    aiSummary: v.string(),
    aiPriority: v.number(),
    findings: v.array(
      v.object({
        type: v.string(),
        severity: v.number(),
        evidence: v.string(),
      })
    ),
    actions: v.array(
      v.object({
        suggestedKey: v.string(),
        title: v.string(),
        description: v.string(),
        reason: v.string(),
        priority: v.number(),
        riskValue: v.number(),
        recommendedSteps: v.array(v.string()),
        estimatedCost: v.number(),
      })
    ),
    createdAt: v.number(),
  })
    .index("by_asset", ["assetId"])
    .index("by_createdAt", ["createdAt"]),

  workOrders: defineTable({
    assetId: v.id("assets"),
    inspectionId: v.id("inspections"),
    title: v.string(),
    status: v.union(
      v.literal("open"),
      v.literal("in_progress"),
      v.literal("blocked"),
      v.literal("done")
    ),
    priority: v.number(),
    assigneeUserId: v.optional(v.id("users")),
    dueAt: v.optional(v.number()),
    createdAt: v.number(),
  }).index("by_asset", ["assetId"]),

  scans: defineTable({
    assetId: v.id("assets"),
    userId: v.id("users"),
    action: v.union(
      v.literal("open_menu"),
      v.literal("report_problem"),
      v.literal("inspect_item"),
      v.literal("report_maintenance")
    ),
    scannedAt: v.number(),
    latitude: v.optional(v.number()),
    longitude: v.optional(v.number()),
  })
    .index("by_asset", ["assetId"])
    .index("by_user", ["userId"]),
});
