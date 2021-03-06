# model settings
model = dict(
    type='RetinaNet',
    pretrained='https://download.pytorch.org/models/mobilenet_v2-b0353104.pth',
    backbone=dict(
        type='MobileNetV2',
        out_indices=(3, 6, 13, 18)),
    neck=dict(
        type='FPN',
        in_channels=[24, 32, 96, 1280],
        out_channels=256,
        start_level=1,
        add_extra_convs=True,
        # norm_cfg=dict(type='BN'),   ###
        # activation='relu',          ###
        num_outs=5),
    bbox_head=dict(
        type='RetinaDwHead',
        num_classes=2,
        in_channels=256,
        stacked_convs=4,
        feat_channels=256,
        octave_base_scale=4,
        scales_per_octave=3,
        anchor_ratios=[0.5, 1.0, 2.0],
        anchor_strides=[8, 16, 32, 64, 128],
        target_means=[.0, .0, .0, .0],
        target_stds=[1.0, 1.0, 1.0, 1.0],
        norm_cfg=dict(type='BN'),   ###
        loss_cls=dict(
            type='FocalLoss',
            use_sigmoid=True,
            gamma=2.0,
            alpha=0.25,
            loss_weight=1.0),
        loss_bbox=dict(type='SmoothL1Loss', beta=0.11, loss_weight=1.0)))
# training and testing settings
train_cfg = dict(
    assigner=dict(
        type='MaxIoUAssigner',
        pos_iou_thr=0.5,
        neg_iou_thr=0.4,
        min_pos_iou=0,
        ignore_iof_thr=-1),
    allowed_border=-1,
    pos_weight=-1,
    debug=False)
test_cfg = dict(
    nms_pre=1000,
    min_bbox_size=0,
    score_thr=0.05,
    nms=dict(type='nms', iou_thr=0.5),
    max_per_img=100)
# dataset settings
dataset_type = 'CervicalCancerDataset'
data_root = 'data/Cervical_Cancer/'
img_norm_cfg = dict(
    mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)
train_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(type='LoadAnnotations', with_bbox=True),
    dict(type='CervicalCancerCrop', crop_size=(800, 800)),
    dict(type='Resize', img_scale=(800, 800), keep_ratio=True),
    dict(type='RandomShiftGtBBox', shift_rate=0.2),
    dict(type='ReplaceBackground', 
        drop_rate=0.2, 
        crop_size=(800, 800),
        background_dir='data/Cervical_Cancer/neg_roi'),
    dict(type='RandomFlip', flip_ratio=0.5),
    dict(type='RandomVerticalFlip', flip_ratio=0.5),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='Pad', size_divisor=32),
    dict(type='DefaultFormatBundle'),
    dict(type='Collect', keys=['img', 'gt_bboxes', 'gt_labels']),
]
test_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(
        type='MultiScaleFlipAug',
        img_scale=(800, 800),
        flip=False,
        transforms=[
            dict(type='Resize', keep_ratio=True),
            # dict(type='RandomFlip'),
            dict(type='Normalize', **img_norm_cfg),
            dict(type='Pad', size_divisor=32),
            dict(type='ImageToTensor', keys=['img']),
            dict(type='Collect', keys=['img']),
        ])
]
data = dict(
    imgs_per_gpu=8,
    workers_per_gpu=16,
    train=dict(
        type=dataset_type,
        ann_file=data_root + 'train/label',
        img_prefix=data_root + 'train/image',
        # ann_file=data_root + 'RoiImage',
        # img_prefix=data_root + 'RoiLabel',
        pipeline=train_pipeline),
    test=dict(
        type=dataset_type,
        ann_file=data_root + 'val/label',
        img_prefix=data_root + 'val/image',
        pipeline=test_pipeline))
# optimizer
optimizer = dict(type='SGD', lr=0.02*(data['imgs_per_gpu']/16), momentum=0.9, weight_decay=0.0001)
optimizer_config = dict(grad_clip=dict(max_norm=35, norm_type=2))
lr_config = dict(
    policy='cosine',
    target_lr=0.00001,
    warmup='linear',
    warmup_iters=500,
    warmup_ratio=1.0 / 3)
checkpoint_config = dict(interval=10)
# yapf:disable
log_config = dict(
    interval=50,
    hooks=[
        dict(type='TextLoggerHook'),
        # dict(type='TensorboardLoggerHook')
    ])
# yapf:enable
# runtime settings
total_epochs = 100
dist_params = dict(backend='nccl')
log_level = 'INFO'


# work_dir = './work_dirs/cervical_cancer/retinanet_mobilenetv2_fpn_dwhead_1x/0_baseline'
work_dir = './work_dirs/cervical_cancer/retinanet_mobilenetv2_fpn_dwhead_1x/2_addBN'


load_from = None
resume_from = 'work_dirs/cervical_cancer/retinanet_mobilenetv2_fpn_dwhead_1x/2_addBN/epoch_70.pth'
workflow = [('train', 1)]
