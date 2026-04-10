#ifndef STEVENAPP_H
#define STEVENAPP_H

#include <NiApplication.h>

class StevenApp : public NiApplication
{
public:
    StevenApp();

    virtual bool Initialize();
    virtual bool CreateScene();
    virtual bool CreateCamera();
    virtual bool CreateRenderer();
    virtual void ProcessInput();
    virtual void UpdateFrame();

protected:
    bool LoadZoneNIF(const char* pcFilename);

    // Camera state (fly camera)
    NiPoint3 m_kCamPos;
    float m_fCamYaw;
    float m_fCamPitch;
    float m_fMoveSpeed;
    float m_fLookSpeed;
};

#endif
