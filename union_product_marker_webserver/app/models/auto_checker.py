"""
自动检查器模块

这个模块负责检查产品标注数据的质量问题，并将问题记录到auto_notes字段。
采用基于类方法的规则系统，支持单个产品检查和批量检查。

设计特点：
1. 每个检查规则都是一个独立的类，使用类方法（@classmethod）
2. 新增规则只需定义新类，无需修改其他代码
3. 系统自动发现和调用所有规则类
4. 支持单个和批量检查

检查规则：
1. 图片检查：主图、图片数量等
2. 价格检查：价格合理性等
3. 品牌检查：品牌信息完整性等
4. 名称检查：统一名称完整性等
5. 其他规则...

作者: Union Product Marker Team
版本: 1.0.0
"""

import json
import inspect
import sys
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from app.utils.db_util import get_db_connection


class BaseRule(ABC):
    """
    基础规则抽象类
    
    所有检查规则都应该继承这个类，并实现check和get_rule_name方法。
    使用类方法（@classmethod）避免实例化，提高性能。
    """
    
    @classmethod
    @abstractmethod
    def check(cls, data: Dict) -> List[str]:
        """
        检查方法，子类必须实现
        
        Args:
            data (Dict): 标注数据字典
            
        Returns:
            List[str]: 问题列表，如果没有问题返回空列表
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_rule_name(cls) -> str:
        """
        获取规则名称，用于错误处理和日志记录
        
        Returns:
            str: 规则名称
        """
        pass


class ImageRule(BaseRule):
    """
    图片检查规则
    
    检查产品图片相关的问题：
    1. 无图
    2. 有图时，没有主图
    3. 有图时，任意图片缺少本地路径
    4. 检查是否使用了fairprice的图片
    """
    
    @classmethod
    def check(cls, data: Dict) -> List[str]:
        issues = []
        images = data.get('images', {})
        image_local_paths = data.get('image_local_paths', {})
        
        # 统计有图片的数量
        image_count = sum(1 for img in images.values() if img)
        
        # 1. 无图
        if image_count == 0:
            issues.append("无图")
            return issues
        
        # 2. 有图时，没有主图
        if not images.get('main'):
            issues.append("无main图")
        
        # 3. 有图时，任意图片缺少本地路径
        for img_type, img_url in images.items():
            if img_url and not image_local_paths.get(img_type):
                issues.append(f"{img_type}图无本地路径")
        
        # 4. 检查是否使用了fairprice的图片
        fairprice_images = []
        for img_type, img_url in images.items():
            if img_url and 'fairprice' in img_url.lower():
                fairprice_images.append(img_type)
        
        if fairprice_images:
            img_types_str = "、".join(fairprice_images)
            issues.append(f"{img_types_str}图来自fairprice")
        
        return issues
    
    @classmethod
    def get_rule_name(cls) -> str:
        return "图片检查"


class PriceRule(BaseRule):
    """
    价格检查规则
    
    检查产品价格相关的问题：
    1. 暂不查是否有价格，后续补充（保持注释掉的状态）
    2. 任意价格不能为负值
    3. 上架价格需要不低于成本价格
    """
    
    @classmethod
    def check(cls, data: Dict) -> List[str]:
        issues = []
        
        price_listed = data.get('price_listed')
        price_cost = data.get('price_cost')
        
        # 1. 暂不查是否有价格，后续补充（保持注释掉的状态）
        #if price_listed is None and price_cost is None:
        #    issues.append("缺少价格信息")
        
        # 2. 任意价格不能为负值
        if price_listed is not None and price_listed < 0:
            issues.append("上架价格<0")
        
        if price_cost is not None and price_cost < 0:
            issues.append("成本价格<0")
        
        # 3. 上架价格需要不低于成本价格
        if price_listed is not None and price_cost is not None:
            if price_listed < price_cost:
                issues.append("上架价格<成本价格")
        
        return issues
    
    @classmethod
    def get_rule_name(cls) -> str:
        return "价格检查"


class BrandRule(BaseRule):
    """
    品牌检查规则
    
    检查产品品牌相关的问题：
    1. 是否有品牌信息
    2. 品牌名称是否过短
    """
    
    @classmethod
    def check(cls, data: Dict) -> List[str]:
        issues = []
        
        brand = data.get('brand', '').strip()
        
        if not brand:
            issues.append("无品牌")
        elif len(brand) < 2:
            issues.append("品牌<2字符）")
        
        return issues
    
    @classmethod
    def get_rule_name(cls) -> str:
        return "品牌检查"


class NameRule(BaseRule):
    """
    名称检查规则
    
    检查产品名称相关的问题：
    1. 是否有统一名称
    2. 统一名称是否过短
    """
    
    @classmethod
    def check(cls, data: Dict) -> List[str]:
        issues = []
        
        unified_name = data.get('unified_name', '').strip()
        
        if not unified_name:
            issues.append("无统一名称")
        elif len(unified_name) < 5:
            issues.append("统一名称<5字符")
        
        return issues
    
    @classmethod
    def get_rule_name(cls) -> str:
        return "名称检查"


class AutoChecker:
    """
    自动检查器主类
    
    负责协调所有检查规则，提供单个和批量检查功能。
    自动发现所有继承自BaseRule的规则类并执行检查。
    """
    
    @classmethod
    def get_all_rules(cls) -> List[type]:
        """
        自动发现所有规则类
        
        通过反射机制找到当前模块中所有继承自BaseRule的类。
        
        Returns:
            List[type]: 所有规则类的列表
        """
        rules = []
        current_module = sys.modules[__name__]
        
        for name, obj in inspect.getmembers(current_module):
            if (inspect.isclass(obj) and 
                issubclass(obj, BaseRule) and 
                obj != BaseRule):
                rules.append(obj)
        
        return rules
    
    @classmethod
    def check_product(cls, annotation_json: str) -> List[str]:
        """
        检查单个产品的标注数据
        
        Args:
            annotation_json (str): 标注数据的JSON字符串
            
        Returns:
            List[str]: 所有问题的列表
        """
        # 解析JSON数据
        try:
            data = json.loads(annotation_json)
        except json.JSONDecodeError:
            return ["标注数据格式错误（JSON解析失败）"]
        except Exception as e:
            return [f"数据解析出错: {str(e)}"]
        
        # 获取所有规则类
        rules = cls.get_all_rules()
        all_issues = []
        
        # 执行每个规则检查
        for rule_class in rules:
            try:
                issues = rule_class.check(data)
                all_issues.extend(issues)
            except Exception as e:
                # 记录规则执行错误，但不影响其他规则
                error_msg = f"{rule_class.get_rule_name()}执行出错: {str(e)}"
                all_issues.append(error_msg)
                print(f"规则执行错误: {error_msg}")
        
        return all_issues
    
    @classmethod
    def check_single_product(cls, product_id: str) -> str:
        """
        检查单个产品并更新数据库
        
        Args:
            product_id (str): 产品ID
            
        Returns:
            str: 检查结果字符串（无问题时返回空字符串）
        """
        db = get_db_connection()
        
        try:
            # 获取产品标注数据
            product = db.execute(
                'SELECT annotation_data FROM products WHERE id = ?', 
                (product_id,)
            ).fetchone()
            
            if not product:
                return "未找到产品"
            
            if not product['annotation_data']:
                return "产品未标注"
            
            # 执行检查
            issues = cls.check_product(product['annotation_data'])
            
            # 更新auto_notes字段（每次都覆盖）
            auto_notes = "; ".join(issues) if issues else ""
            db.execute(
                'UPDATE products SET auto_notes = ? WHERE id = ?',
                (auto_notes, product_id)
            )
            db.commit()
            
            return auto_notes
            
        except Exception as e:
            db.rollback()
            error_msg = f"检查产品时出错: {str(e)}"
            print(error_msg)
            return error_msg
        finally:
            db.close()
    
    @classmethod
    def check_all_products(cls) -> Dict[str, int]:
        """
        批量检查所有已标注的产品
        
        Returns:
            Dict[str, int]: 检查统计结果
                - total: 总产品数
                - checked: 成功检查数
                - errors: 检查出错数
        """
        db = get_db_connection()
        
        try:
            # 获取所有已标注的产品
            products = db.execute(
                'SELECT id, annotation_data FROM products WHERE annotation_data IS NOT NULL AND annotation_data != ""'
            ).fetchall()
            
            total_count = len(products)
            checked_count = 0
            error_count = 0
            
            # 逐个检查产品
            for product in products:
                try:
                    issues = cls.check_product(product['annotation_data'])
                    auto_notes = "; ".join(issues) if issues else ""
                    
                    db.execute(
                        'UPDATE products SET auto_notes = ? WHERE id = ?',
                        (auto_notes, product['id'])
                    )
                    checked_count += 1
                    
                except Exception as e:
                    error_count += 1
                    print(f"检查产品 {product['id']} 时出错: {e}")
            
            db.commit()
            
            return {
                'total': total_count,
                'checked': checked_count,
                'errors': error_count
            }
            
        except Exception as e:
            db.rollback()
            print(f"批量检查时出错: {e}")
            return {
                'total': 0,
                'checked': 0,
                'errors': 1
            }
        finally:
            db.close()


# 创建全局实例，方便在其他模块中使用
auto_checker = AutoChecker() 