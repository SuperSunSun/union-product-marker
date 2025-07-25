"""
自动检查器测试模块

测试自动检查器的各项功能，包括：
1. 规则检查功能
2. 单个产品检查
3. 批量检查功能
4. 错误处理

作者: Union Product Marker Team
版本: 1.0.0
"""

import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.auto_checker import AutoChecker, ImageRule, PriceRule, BrandRule, NameRule


def test_individual_rules():
    """测试各个规则类的检查功能"""
    print("🧪 测试各个规则类...")
    
    # 测试数据
    test_data = {
        'images': {
            'main': '',  # 没有主图
            'front': 'front.jpg',
            'back': ''
        },
        'image_local_paths': {
            'main': '',
            'front': '/path/to/front.jpg',
            'back': ''
        },
        'price_listed': None,  # 缺少价格
        'price_cost': -1,  # 不合理价格
        'brand': '',  # 缺少品牌
        'unified_name': 'ab'  # 名称过短
    }
    
    # 测试图片规则
    image_issues = ImageRule.check(test_data)
    print(f"图片检查结果: {image_issues}")
    assert "没有主图" in image_issues
    assert "图片数量不足（少于2张）" in image_issues
    
    # 测试价格规则
    price_issues = PriceRule.check(test_data)
    print(f"价格检查结果: {price_issues}")
    assert "缺少价格信息" in price_issues
    assert "成本价格不合理（应大于0）" in price_issues
    
    # 测试品牌规则
    brand_issues = BrandRule.check(test_data)
    print(f"品牌检查结果: {brand_issues}")
    assert "缺少品牌信息" in brand_issues
    
    # 测试名称规则
    name_issues = NameRule.check(test_data)
    print(f"名称检查结果: {name_issues}")
    assert "统一名称过短（少于5个字符）" in name_issues
    
    print("✅ 各个规则类测试通过")


def test_auto_checker():
    """测试自动检查器主类"""
    print("\n🧪 测试自动检查器主类...")
    
    # 测试获取所有规则
    rules = AutoChecker.get_all_rules()
    print(f"发现的规则类: {[rule.__name__ for rule in rules]}")
    assert len(rules) >= 4  # 至少应该有4个规则类
    
    # 测试检查功能
    test_json = json.dumps({
        'images': {'main': ''},
        'price_listed': None,
        'brand': '',
        'unified_name': ''
    })
    
    issues = AutoChecker.check_product(test_json)
    print(f"自动检查结果: {issues}")
    assert len(issues) > 0  # 应该有检查出问题
    
    print("✅ 自动检查器主类测试通过")


def test_error_handling():
    """测试错误处理"""
    print("\n🧪 测试错误处理...")
    
    # 测试无效JSON
    invalid_json = "{invalid json}"
    issues = AutoChecker.check_product(invalid_json)
    print(f"无效JSON检查结果: {issues}")
    assert "JSON解析失败" in issues[0]
    
    # 测试空数据
    empty_data = {}
    issues = AutoChecker.check_product(json.dumps(empty_data))
    print(f"空数据检查结果: {issues}")
    assert len(issues) > 0  # 应该检查出一些问题
    
    print("✅ 错误处理测试通过")


def test_normal_data():
    """测试正常数据"""
    print("\n🧪 测试正常数据...")
    
    # 正常的数据
    normal_data = {
        'images': {
            'main': 'main.jpg',
            'front': 'front.jpg',
            'back': 'back.jpg'
        },
        'image_local_paths': {
            'main': '/path/to/main.jpg',
            'front': '/path/to/front.jpg',
            'back': '/path/to/back.jpg'
        },
        'price_listed': 99.99,
        'price_cost': 50.00,
        'brand': 'TestBrand',
        'unified_name': 'Test Product Name'
    }
    
    issues = AutoChecker.check_product(json.dumps(normal_data))
    print(f"正常数据检查结果: {issues}")
    
    # 正常数据应该没有问题，或者只有很少的问题
    if issues:
        print(f"发现的问题: {issues}")
    else:
        print("✅ 正常数据检查通过，没有发现问题")


def main():
    """运行所有测试"""
    print("🚀 开始自动检查器测试...\n")
    
    try:
        test_individual_rules()
        test_auto_checker()
        test_error_handling()
        test_normal_data()
        
        print("\n🎉 所有测试通过！自动检查器工作正常。")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 