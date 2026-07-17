import type { Config } from 'drizzle-kit';
import path from 'path';

const dbPath = path.resolve(__dirname, '../data/database/learning.db');

export default {
  schema: './src/db/schema.ts',
  out: './drizzle',
  dialect: 'sqlite',
  dbCredentials: {
    url: dbPath,
  },
} satisfies Config;
