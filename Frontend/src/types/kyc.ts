export type ImageAsset = {
  uri: string;
  name: string;
  type: string;
};

export type KycUploadPayload = {
  nationalId: string;
  residentialAddress: string;
  idFront: ImageAsset;
  idBack: ImageAsset;
  selfie: ImageAsset;
};

export type KycRecord = {
  id: number;
  userId: number;
  nationalIdNumber: string;
  documentType: string;
  residentialAddress: string | null;
  documentFront: string;
  documentBack: string | null;
  selfieImage: string | null;
  status: string;
  rejectionReason: string | null;
  createdAt: string | null;
};
