from facefusion.types import Locales

LOCALES : Locales =\
{
	'en':
	{
		'help':
		{
			'model': 'choose the model responsible for colorizing the frame',
			'size': 'specify the frame size provided to the frame colorizer',
			'blend': 'blend the colorized into the previous frame'
		},
		'uis':
		{
			'blend_slider': 'FRAME COLORIZER BLEND',
			'model_dropdown': 'FRAME COLORIZER MODEL',
			'size_dropdown': 'FRAME COLORIZER SIZE'
		}
	},
	'zh':
	{
		'help':
		{
			'model': '选择负责帧着色的模型',
			'size': '指定提供给帧着色器的帧大小',
			'blend': '将着色后的帧混合到原帧'
		},
		'uis':
		{
			'blend_slider': '帧着色混合',
			'model_dropdown': '帧着色模型',
			'size_dropdown': '帧着色大小'
		}
	}
}
