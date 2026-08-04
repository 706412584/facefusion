from facefusion.types import Locales

LOCALES : Locales =\
{
	'en':
	{
		'help':
		{
			'model': 'choose the model responsible for enhancing the face',
			'blend': 'blend the enhanced into the previous face',
			'weight': 'specify the degree of weight applied to the face'
		},
		'uis':
		{
			'blend_slider': 'FACE ENHANCER BLEND',
			'model_dropdown': 'FACE ENHANCER MODEL',
			'weight_slider': 'FACE ENHANCER WEIGHT'
		}
	},
	'zh':
	{
		'help':
		{
			'model': '选择负责人脸增强的模型',
			'blend': '将增强后的人脸混合到原人脸',
			'weight': '指定应用于人脸的权重程度'
		},
		'uis':
		{
			'blend_slider': '人脸增强混合',
			'model_dropdown': '人脸增强模型',
			'weight_slider': '人脸增强权重'
		}
	}
}
