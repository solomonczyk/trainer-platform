#!/usr/bin/env python3
"""CLI script to seed the BA trainer package into the database.

Usage:
    python scripts/seed_ba_trainer.py

Requires the backend environment to be configured (DATABASE_URL).
Run from the project root directory.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings
from app.modules.admin.ba_trainer_seed import seed_ba_trainer


async def main():
    print("=" * 60)
    print("BA Trainer Package Seeder")
    print("=" * 60)
    print(f"Database: {settings.database_url}")
    print()

    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        try:
            results = await seed_ba_trainer(session)
            await session.commit()
            print("Seeding completed successfully!")
            print()
            for key, value in results.items():
                print(f"  {key}: {value}")
        except Exception as e:
            await session.rollback()
            print(f"ERROR: Seeding failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
