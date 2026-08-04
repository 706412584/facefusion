from facefusion.types import Locales

LOCALES : Locales =\
{
	'en':
	{
		'help':
		{
			'model': 'choose the model responsible for swapping the face',
			'pixel_boost': 'choose the pixel boost resolution for the face swapper',
			'weight': 'specify the degree of weight applied to the face'
		},
		'uis':
		{
			'model_dropdown': 'FACE SWAPPER MODEL',
			'pixel_boost_dropdown': 'FACE SWAPPER PIXEL BOOST',
			'weight_slider': 'FACE SWAPPER WEIGHT'
		}
	},
	'zh':
	{
		'help':
		{
			'model': '选择负责人脸交换的模型',
			'pixel_boost': '选择人脸交换的像素增强分辨率',
			'weight': '指定应用于人脸的权重程度'
		},
		'uis':
		{
			'model_dropdown': '人脸交换模型',
			'pixel_boost_dropdown': '人脸交换像素增强',
			'weight_slider': '人脸交换权重'
		}
	}
}
