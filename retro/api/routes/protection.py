from fastapi import APIRouter
from retro.protection.firewall_manager import firewall_manager
from retro.protection.geo_blocker import geo_blocker
from retro.protection.dns_sinkhole import dns_sinkhole
from retro.protection.ip_reputation import ip_reputation

router = APIRouter(prefix="/protection", tags=["protection"])


@router.get("")
async def get_protection_status():
    return {
        "blocked_ips": await firewall_manager.get_blocked_ips(),
        "blocked_countries": geo_blocker.get_blocked_countries(),
        "blocked_domains": dns_sinkhole.get_blocked_domains(),
    }


@router.post("/block/{ip}")
async def block_ip(ip: str):
    success = await firewall_manager.block_ip(ip)
    return {"status": "blocked" if success else "failed", "ip": ip}


@router.post("/unblock/{ip}")
async def unblock_ip(ip: str):
    success = await firewall_manager.unblock_ip(ip)
    return {"status": "unblocked" if success else "failed", "ip": ip}


@router.get("/reputation/{ip}")
async def check_reputation(ip: str):
    score = await ip_reputation.check(ip)
    return {"ip": ip, "reputation_score": score}


@router.post("/geo/block/{country}")
async def block_country(country: str):
    geo_blocker.block_country(country)
    return {"status": "blocked", "country": country}


@router.post("/geo/unblock/{country}")
async def unblock_country(country: str):
    geo_blocker.unblock_country(country)
    return {"status": "unblocked", "country": country}


@router.post("/dns/block/{domain}")
async def block_domain(domain: str):
    dns_sinkhole.block_domain(domain)
    return {"status": "blocked", "domain": domain}


@router.post("/dns/unblock/{domain}")
async def unblock_domain(domain: str):
    dns_sinkhole.unblock_domain(domain)
    return {"status": "unblocked", "domain": domain}
