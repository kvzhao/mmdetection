# model settings

date = '2020-03-03'
task = 'retinanet_free_anchor_r34_fpn_1x'

model = dict(
    type='RetinaNet',
    pretrained='torchvision://resnet34',
    backbone=dict(
        type='ResNet',
        depth=34,
        num_stages=4,
        out_indices=(0, 1, 2, 3),
        frozen_stages=1,
        style='pytorch'),
    neck=dict(
        type='FPN',
        in_channels=[64, 128, 256, 512],
        out_channels=256,
        start_level=1,
        add_extra_convs=True,
        num_outs=5),
    bbox_head=dict(
        type='FreeAnchorRetinaHead',
        num_classes=2,
        in_channels=256,
        stacked_convs=4,
        feat_channels=256,
        octave_base_scale=4,
        scales_per_octave=3,
        anchor_ratios=[0.5, 1.0, 2.0],
        anchor_strides=[8, 16, 32, 64, 128],
        target_means=[.0, .0, .0, .0],
        target_stds=[0.1, 0.1, 0.2, 0.2],
        loss_bbox=dict(type='SmoothL1Loss', beta=0.11, loss_weight=0.75)))
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
    nms_pre=6000,
    debug=False)
test_cfg = dict(
    nms_pre=6000,
    min_bbox_size=0,
    score_thr=0.05,
    nms=dict(type='nms', iou_thr=0.5),
    max_per_img=100)
# dataset settings
dataset_type = 'CrowdhumanDataset'
data_root = '/home/kv_zhao/datasets/CrowdHuman/'
img_norm_cfg = dict(
    mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)
train_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(type='LoadAnnotations', with_bbox=True),
    dict(type='Resize', img_scale=(640, 640), keep_ratio=True),
    dict(type='RandomFlip', flip_ratio=0.5),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='Pad', size_divisor=32),
    dict(type='DefaultFormatBundle'),
    dict(type='Collect', keys=['img', 'gt_bboxes', 'gt_labels']),
]
test_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(
        type='MultiScaleFlipAug',
        img_scale=(640, 640),
        flip=False,
        transforms=[
            dict(type='Resize', keep_ratio=True),
            dict(type='RandomFlip'),
            dict(type='Normalize', **img_norm_cfg),
            dict(type='Pad', size_divisor=32),
            dict(type='ImageToTensor', keys=['img']),
            dict(type='Collect', keys=['img']),
        ])
]
data = dict(
    imgs_per_gpu=32,
    workers_per_gpu=16,
    train=dict(
        type=dataset_type,
        ann_file=data_root + 'annotations/train.json',
        img_prefix=data_root + 'Images/',
        pipeline=train_pipeline),
    val=dict(
        type=dataset_type,
        ann_file=data_root + 'annotations/validation.json',
        img_prefix=data_root + 'Images/',
        pipeline=test_pipeline),
    test=dict(
        type=dataset_type,
        ann_file=data_root + 'annotations/validation.json',
        img_prefix=data_root + 'Images/',
        pipeline=test_pipeline))
# optimizer
optimizer = dict(type='SGD', lr=0.01, momentum=0.9, weight_decay=0.0001)
optimizer_config = dict(grad_clip=dict(max_norm=35, norm_type=2))
# learning policy
lr_config = dict(
    policy='step',
    warmup='linear',
    warmup_iters=500,
    warmup_ratio=1.0 / 3,
    step=[15, 19])
checkpoint_config = dict(interval=1)
# yapf:disable
log_config = dict(
    interval=50,
    hooks=[
        dict(type='TextLoggerHook'),
        # dict(type='TensorboardLoggerHook')
    ])
# yapf:enable
# runtime settings
total_epochs = 20
device_ids = range(8)
dist_params = dict(backend='nccl')
log_level = 'INFO'
work_dir = './work_dirs/crowdhuman/{}/{}/'.format(date, task)
load_from = None
resume_from = None
workflow = [('train', 1)]
