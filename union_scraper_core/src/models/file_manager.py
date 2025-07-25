"""
File naming model for managing file names across the application
"""

class FileManager:
    """文件名管理器，负责生成不同类型文件的标准文件名"""
    
    def __init__(self, prefix: str, product_id: str, url_tag: str = "main"):
        """
        初始化文件名管理器
        :param prefix: 文件名前缀，用于区分不同网站的文件（如 'a' 代表 amazon）
        :param product_id: 商品ID
        """
        self.prefix = prefix
        self.url_tag = url_tag
        self.product_id = str(product_id)
    
    
    def _get_filename_suffix(self) -> str:
        """
        获取文件名后缀
        :return: 文件名后缀
        """
        return f"_{self.url_tag}" if self.url_tag != "main" else ""
    
    def get_html_filename(self) -> str:
        """生成HTML文件名"""
        suffix = self._get_filename_suffix()
        return f"{self.prefix}_{self.product_id}{suffix}.html"
    
    def get_json_filename(self) -> str:
        """生成JSON文件名"""
        suffix = self._get_filename_suffix()
        return f"{self.prefix}_{self.product_id}{suffix}.json"
    
    def get_image_filename(self, index: int) -> str:
        """生成图片文件名"""
        suffix = self._get_filename_suffix()
        return f"{self.prefix}_{self.product_id}{suffix}_{index}.jpg"
    
    def get_product_folder(self) -> str:
        """
        生成商品文件夹名，直接使用商品ID作为文件夹名
        :return: 商品文件夹名
        """
        return self.product_id 