"""
Pydantic 数据模型定义示例

用于结构化信息提取
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class ProcurementInfo(BaseModel):
    """政府采购信息提取模型"""
    
    # purchaser: Optional[str] = Field(
    #     None, 
    #     description="采购方名称（发起采购的单位，如医院或政府部门）"
    # )
    
    # winner: Optional[str] = Field(
    #     None, 
    #     description="中标商名称（赢得合同的公司）"
    # )
    
    item_name: Optional[str] = Field(
        None, 
        description="采购物品名称（本次采购的核心项目或物品）"
    )
    
    quantity: Optional[int] = Field(
        None, 
        ge=0,
        description="采购物品数量（必须是非负整数）"
    )
    
    amount: Optional[float] = Field(
        None,
        ge=0,
        description="中标金额，单位为元（必须是非负数）"
    )

    device: Optional[bool] = Field(
        None,
        description="是否为设备采购（True表示采购设备如医疗设备，False表示采购非设备如药品等）"
    )

    class Config:
        json_schema_extra = {
            "example": {
                # "purchaser": "某市人民医院",
                # "winner": "某医疗设备有限公司",
                "item_name": "医疗设备",
                "quantity": 10,
                "amount": 150000.0,
                "device": True
            }
        }