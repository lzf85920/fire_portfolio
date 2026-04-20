"""Clear all data from database while keeping table structure"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_database():
    """Clear all data from database tables while preserving schema"""
    from config import DATABASE_URL
    from database.schema import (
        TransactionModel, PerformanceSnapshotModel, 
        PriceHistoryModel, HoldingModel, PortfolioModel
    )
    
    try:
        engine = create_engine(DATABASE_URL, echo=False)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Delete records in order of foreign key dependencies
        logger.info("🗑️  開始清空數據庫...")
        
        # Clear transactions first (references portfolios)
        transaction_count = session.query(TransactionModel).delete()
        session.commit()
        logger.info(f"  ✓ 已清空交易記錄: {transaction_count} 筆")
        
        # Clear performance snapshots (references portfolios)
        snapshot_count = session.query(PerformanceSnapshotModel).delete()
        session.commit()
        logger.info(f"  ✓ 已清空性能快照: {snapshot_count} 筆")
        
        # Clear price history (independent table)
        price_count = session.query(PriceHistoryModel).delete()
        session.commit()
        logger.info(f"  ✓ 已清空價格歷史: {price_count} 筆")
        
        # Clear holdings (references portfolios)
        holding_count = session.query(HoldingModel).delete()
        session.commit()
        logger.info(f"  ✓ 已清空持倉: {holding_count} 筆")
        
        # Clear portfolios (parent table)
        portfolio_count = session.query(PortfolioModel).delete()
        session.commit()
        logger.info(f"  ✓ 已清空投資組合: {portfolio_count} 筆")
        
        session.close()
        logger.info("✅ 數據庫已成功清空（表結構已保留）")
        return True
        
    except Exception as e:
        logger.error(f"❌ 無法清空數據庫: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("數據庫清除工具")
    logger.info("=" * 50)
    
    if clear_database():
        logger.info("=" * 50)
        logger.info("✅ 操作完成！所有數據已清除")
        logger.info("=" * 50)
    else:
        logger.error("❌ 清除數據庫失敗")
