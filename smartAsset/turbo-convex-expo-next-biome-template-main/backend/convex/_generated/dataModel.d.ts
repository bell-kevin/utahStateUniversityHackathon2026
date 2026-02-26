// Temporary stub. Regenerate with `convex codegen`.
export type Tables = {
  messages: {
    body: string;
    createdAt: number;
  };
};

export type Doc<Table extends keyof Tables> = Tables[Table] & { _id: Id<Table> };
export type Id<Table extends keyof Tables> = string & { __table: Table };
