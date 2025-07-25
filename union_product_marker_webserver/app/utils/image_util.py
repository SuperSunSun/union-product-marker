"""
图片处理工具模块

这个模块提供图片处理功能，包括：
1. 图片resize到指定尺寸
2. 图片格式转换和压缩
3. 特殊图片处理（正方形/长方形）
4. 批量图片处理

主要功能：
- 将图片resize到800x800px
- 正方形图：短边填充白色
- 长方形图：按比例缩放，长边80%，两侧各补充10%
- 无损压缩，导出为jpg格式

作者: Union Product Marker Team
版本: 1.0.0
"""

import os
from PIL import Image, ImageOps
import logging

class ImageProcessor:
    """
    图片处理器类
    
    负责处理图片的resize、压缩、格式转换等操作。
    """
    
    def __init__(self):
        """初始化图片处理器"""
        self.target_size = (800, 800)
        self.quality = 95  # JPEG压缩质量
        self.padding_ratio = 0.2  # 长方形图的padding比例（20%）
    
    def process_image(self, input_path, output_path, target_size=None):
        """
        处理单张图片
        
        Args:
            input_path (str): 输入图片路径
            output_path (str): 输出图片路径
            target_size (tuple): 目标尺寸，默认(800, 800)
            
        Returns:
            bool: 处理是否成功
        """
        try:
            if target_size is None:
                target_size = self.target_size
            
            # 打开图片
            with Image.open(input_path) as img:
                # 转换为RGB模式（确保兼容性）
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 获取原始尺寸
                original_width, original_height = img.size
                
                # 判断图片类型并处理
                if self._is_square_image(original_width, original_height):
                    # 正方形图片处理
                    processed_img = self._process_square_image(img, target_size)
                else:
                    # 长方形图片处理
                    processed_img = self._process_rectangle_image(img, target_size)
                
                # 确保输出目录存在
                output_dir = os.path.dirname(output_path)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                # 保存图片
                processed_img.save(
                    output_path, 
                    'JPEG', 
                    quality=self.quality, 
                    optimize=True
                )
                
                return True
                
        except Exception as e:
            logging.error(f"图片处理失败: {input_path} -> {output_path}, 错误: {str(e)}")
            return False
    
    def _is_square_image(self, width, height):
        """
        判断是否为正方形图片
        
        Args:
            width (int): 图片宽度
            height (int): 图片高度
            
        Returns:
            bool: 是否为正方形（长宽差值小于100px）
        """
        return abs(width - height) < 100
    
    def _process_square_image(self, img, target_size):
        """
        处理正方形图片
        
        短边填充白色直到与长边相同，然后resize到目标尺寸。
        
        Args:
            img (PIL.Image): 输入图片
            target_size (tuple): 目标尺寸
            
        Returns:
            PIL.Image: 处理后的图片
        """
        width, height = img.size
        
        # 确定目标尺寸（取长边）
        max_side = max(width, height)
        
        # 创建白色背景
        background = Image.new('RGB', (max_side, max_side), (255, 255, 255))
        
        # 计算居中位置
        x_offset = (max_side - width) // 2
        y_offset = (max_side - height) // 2
        
        # 将原图粘贴到背景上
        background.paste(img, (x_offset, y_offset))
        
        # resize到目标尺寸
        return background.resize(target_size, Image.Resampling.LANCZOS)
    
    def _process_rectangle_image(self, img, target_size):
        """
        处理长方形图片
        
        锁定比例缩放到长边为800的80%，然后长边两侧各补充10%的长度到800，
        短边向两侧补充到800，补充的部分是白色。
        
        Args:
            img (PIL.Image): 输入图片
            target_size (tuple): 目标尺寸
            
        Returns:
            PIL.Image: 处理后的图片
        """
        width, height = img.size
        target_width, target_height = target_size
        
        # 计算缩放后的尺寸（长边为800的80%）
        scale_ratio = (target_width * (1 - self.padding_ratio)) / max(width, height)
        scaled_width = int(width * scale_ratio)
        scaled_height = int(height * scale_ratio)
        
        # 缩放图片
        scaled_img = img.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)
        
        # 创建白色背景
        background = Image.new('RGB', target_size, (255, 255, 255))
        
        # 计算居中位置
        x_offset = (target_width - scaled_width) // 2
        y_offset = (target_height - scaled_height) // 2
        
        # 将缩放后的图片粘贴到背景上
        background.paste(scaled_img, (x_offset, y_offset))
        
        return background
    
    def batch_process(self, input_files, output_dir, target_size=None):
        """
        批量处理图片
        
        Args:
            input_files (list): 输入文件路径列表
            output_dir (str): 输出目录
            target_size (tuple): 目标尺寸
            
        Returns:
            dict: 处理结果统计
        """
        if target_size is None:
            target_size = self.target_size
        
        results = {
            'total': len(input_files),
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        for input_file in input_files:
            try:
                # 生成输出文件名
                filename = os.path.basename(input_file)
                name, ext = os.path.splitext(filename)
                output_filename = f"{name}.jpg"
                output_path = os.path.join(output_dir, output_filename)
                
                # 处理图片
                if self.process_image(input_file, output_path, target_size):
                    results['success'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"处理失败: {input_file}")
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"处理异常: {input_file} - {str(e)}")
        
        return results
    
    def get_image_info(self, image_path):
        """
        获取图片信息
        
        Args:
            image_path (str): 图片路径
            
        Returns:
            dict: 图片信息
        """
        try:
            with Image.open(image_path) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'mode': img.mode,
                    'format': img.format,
                    'size_bytes': os.path.getsize(image_path)
                }
        except Exception as e:
            return {'error': str(e)} 