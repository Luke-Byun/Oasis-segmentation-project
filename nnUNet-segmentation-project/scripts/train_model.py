import os
import argparse
import torch
from nnunetv2.run.run_training import run_training

"""
[nnU-Net Training Script]
이 스크립트는 터미널 명령어(CLI) 대신 파이썬 코드로 nnU-Net 학습을 실행합니다.
IDE(PyCharm, VS Code)에서 디버깅하거나, Colab 등에서 실행할 때 유용합니다.

Usage:
    python scripts/train_model.py --dataset_id 501 --fold 0
"""

def setup_environment():
    """
    환경 변수가 설정되지 않았을 경우 기본 경로를 설정합니다.
    본인의 환경에 맞게 경로를 수정하세요.
    """
    if 'nnUNet_raw' not in os.environ:
        os.environ['nnUNet_raw'] = "../data/nnUNet_raw"
    if 'nnUNet_preprocessed' not in os.environ:
        os.environ['nnUNet_preprocessed'] = "../data/nnUNet_preprocessed"
    if 'nnUNet_results' not in os.environ:
        os.environ['nnUNet_results'] = "../data/nnUNet_results"
    
    print(f"✅ Environment Variables Checked:")
    print(f"   - raw: {os.environ['nnUNet_raw']}")
    print(f"   - preprocessed: {os.environ['nnUNet_preprocessed']}")
    print(f"   - results: {os.environ['nnUNet_results']}")

def main():
    parser = argparse.ArgumentParser(description="Run nnU-Net Training via Python")
    
    # 기본 설정값 (Decathlon Hippocampus Task 기준)
    parser.add_argument('--dataset_id', type=str, default='501', help='Dataset ID (e.g., 501)')
    parser.add_argument('--configuration', type=str, default='3d_fullres', help='Configuration (2d, 3d_fullres, etc.)')
    parser.add_argument('--fold', type=int, default=0, help='Fold number (0-4)')
    parser.add_argument('--trainer', type=str, default='nnUNetTrainer', help='Trainer class name')
    parser.add_argument('--plans', type=str, default='nnUNetPlans', help='Plans identifier')
    
    args = parser.parse_args()

    # 1. 환경 변수 설정
    setup_environment()

    # 2. GPU 확인
    if torch.cuda.is_available():
        print(f"🚀 Training on GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("⚠️ Warning: No GPU found. Training might be extremely slow.")

    print(f"🧠 Starting Training: Dataset {args.dataset_id} | Fold {args.fold} | Config {args.configuration}")

    # 3. nnU-Net 학습 함수 호출
    # (CLI의 'nnUNetv2_train' 명령어와 동일한 동작을 수행하는 내부 함수입니다)
    try:
        run_training(
            dataset_name_or_id=args.dataset_id,
            configuration=args.configuration,
            fold=args.fold,
            trainer_class_name=args.trainer,
            plans_identifier=args.plans,
            pretrained_weights=None,    # 필요시 경로 입력
            num_gpus=1,                 # 사용할 GPU 개수
            use_compressed_data=False,  
            export_validation_probabilities=False,
            continue_training=False,    # 중단된 학습 이어하기 여부
            only_run_validation=False,
            disable_checkpointing=False,
            val_with_best=False,
            device=torch.device('cuda')
        )
        print("✅ Training Completed Successfully!")

    except Exception as e:
        print(f"❌ Error during training: {e}")
        raise e

if __name__ == "__main__":
    main()