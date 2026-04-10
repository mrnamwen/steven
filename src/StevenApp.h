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
    // Scene objects
    NiNodePtr m_spTriNode;

    // Camera orbit state
    float m_fCamDistance;
    float m_fCamYaw;
    float m_fCamPitch;
    NiPoint3 m_kCamTarget;
};

#endif
